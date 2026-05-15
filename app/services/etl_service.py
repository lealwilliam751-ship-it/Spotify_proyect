"""
filename: etl_service.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Servicio ETL para procesar historial de escucha de Spotify y cargarlo en el DWH.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import DimUser, DimArtist, DimTrack, FactListeningHistory, EtlAudit
from app.services.spotify_service import get_recently_played

def run_etl_process(db: Session, user: DimUser) -> dict:
    """
    Ejecuta el proceso ETL completo para un usuario:
    1. Obtiene tracks recientes de Spotify
    2. Procesa cada track: busca/crea artista y track en dims
    3. Inserta en fact_listening_history
    4. Registra auditoría en etl_audit
    
    Returns:
        Diccionario con estadísticas del proceso
    """
    started_at = datetime.utcnow()
    
    # Inicializar contadores
    users_new = 0  # No aplicable aquí, pero por consistencia
    artists_new = 0
    artists_skipped = 0
    tracks_new = 0
    tracks_skipped = 0
    history_new = 0
    history_skipped = 0
    
    error_message = None
    cursor_after_ms = None
    cursor_next_ms = None
    
    try:
        # 1. Obtener tracks recientes de Spotify
        items = get_recently_played(
            access_token=user.spotify_access_token, 
            limit=50, 
            refresh_token=user.spotify_refresh_token, 
            db=db, 
            user=user
        )
        # 2. Procesar cada item
        for item in items:
            track_data = item["track"]
            played_at_str = item["played_at"]
            played_at = datetime.fromisoformat(played_at_str.replace('Z', '+00:00'))
            
            # Extraer datos clave
            track_spotify_id = track_data["id"]
            track_name = track_data["name"]
            duration_ms = track_data["duration_ms"]
            explicit = track_data["explicit"]
            album_name = track_data["album"]["name"]
            popularity = track_data.get("popularity", 0)
            
            # Primer artista (Spotify devuelve lista, tomamos el primero)
            artist_data = track_data["artists"][0] if track_data["artists"] else {}
            artist_spotify_id = artist_data.get("id")
            artist_name = artist_data.get("name", "Unknown")
            artist_popularity = artist_data.get("popularity", 0)
            artist_followers = artist_data.get("followers", {}).get("total", 0)
            artist_genres = artist_data.get("genres", [])
            
            # --- PROCESAR ARTISTA ---
            artist = db.query(DimArtist).filter(DimArtist.spotify_id == artist_spotify_id).first()
            if not artist:
                artist = DimArtist(
                    spotify_id=artist_spotify_id,
                    name=artist_name,
                    popularity=artist_popularity,
                    followers_count=artist_followers,
                    genres=artist_genres,
                    loaded_at=datetime.utcnow()
                )
                db.add(artist)
                db.flush()  # Para obtener ID sin commit aún
                artists_new += 1
            else:
                artists_skipped += 1
            
            # --- PROCESAR TRACK ---
            track = db.query(DimTrack).filter(DimTrack.spotify_id == track_spotify_id).first()
            if not track:
                track = DimTrack(
                    spotify_id=track_spotify_id,
                    name=track_name,
                    artist_id=artist.artist_id,  # Usamos el ID recién obtenido o existente
                    album_name=album_name,
                    duration_ms=duration_ms,
                    popularity=popularity,
                    explicit=explicit,
                    loaded_at=datetime.utcnow()
                )
                db.add(track)
                db.flush()
                tracks_new += 1
            else:
                tracks_skipped += 1
            
            # --- INSERTAR EN FACT LISTENING HISTORY ---
            # Verificar si ya existe este registro (evitar duplicados por user_id + played_at)
            existing_history = db.query(FactListeningHistory).filter(
                FactListeningHistory.user_id == user.user_id,
                FactListeningHistory.played_at == played_at
            ).first()
            
            if not existing_history:
                # Calcular hour_of_day y day_of_week
                hour_of_day = played_at.hour
                day_of_week = played_at.strftime("%A")  # Lunes, Martes, etc.
                
                history_record = FactListeningHistory(
                    user_id=user.user_id,
                    track_id=track.track_id,
                    artist_id=artist.artist_id,
                    played_at=played_at,
                    hour_of_day=hour_of_day,
                    day_of_week=day_of_week,
                    context_type="player"  # Por defecto, podría venir de Spotify
                )
                db.add(history_record)
                history_new += 1
            else:
                history_skipped += 1
        
        # Commit final de todos los cambios
        db.commit()
        
        finished_at = datetime.utcnow()
        duration_ms_total = int((finished_at - started_at).total_seconds() * 1000)
        
        # Registrar auditoría
        audit_record = EtlAudit(
            spotify_user_id=user.spotify_id,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms_total,
            status="success",
            users_new=users_new,
            artists_new=artists_new,
            artists_skipped=artists_skipped,
            tracks_new=tracks_new,
            tracks_skipped=tracks_skipped,
            history_new=history_new,
            history_skipped=history_skipped,
            cursor_after_ms=None,  # No usamos cursores en esta versión simple
            cursor_next_ms=None
        )
        db.add(audit_record)
        db.commit()
        
        return {
            "status": "success",
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "duration_ms": duration_ms_total,
            "records_processed": len(items),
            "artists_new": artists_new,
            "artists_skipped": artists_skipped,
            "tracks_new": tracks_new,
            "tracks_skipped": tracks_skipped,
            "history_new": history_new,
            "history_skipped": history_skipped
        }
        
    except Exception as e:
        db.rollback()
        finished_at = datetime.utcnow()
        duration_ms_total = int((finished_at - started_at).total_seconds() * 1000)
        error_message = str(e)
        
        # Registrar auditoría de fallo
        audit_record = EtlAudit(
            spotify_user_id=user.spotify_id,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=duration_ms_total,
            status="failed",
            error_message=error_message,
            users_new=users_new,
            artists_new=artists_new,
            artists_skipped=artists_skipped,
            tracks_new=tracks_new,
            tracks_skipped=tracks_skipped,
            history_new=history_new,
            history_skipped=history_skipped,
            cursor_after_ms=None,
            cursor_next_ms=None
        )
        db.add(audit_record)
        db.commit()
        
        raise