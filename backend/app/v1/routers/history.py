"""
filename: history.py
description: Router para consultar el historial de escucha almacenado en la tabla fact_listening_history.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, ListeningHistory
from app.v1.deps import get_current_user

from sqlalchemy import func

router = APIRouter()

@router.get("/recently-played")
async def get_recently_played(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna el historial de escucha del usuario actual."""
    return db.query(ListeningHistory).filter(
        ListeningHistory.user_id == current_user.user_id
    ).order_by(ListeningHistory.played_at.desc()).all()

@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna estadísticas agregadas para el dashboard."""
    # Total de reproducciones
    total_plays = db.query(func.count(ListeningHistory.id)).filter(
        ListeningHistory.user_id == current_user.user_id
    ).scalar() or 0

    # Total de artistas únicos
    total_artists = db.query(func.count(func.distinct(ListeningHistory.artist_id))).filter(
        ListeningHistory.user_id == current_user.user_id
    ).scalar() or 0

    # Total de canciones únicas
    total_tracks = db.query(func.count(func.distinct(ListeningHistory.track_id))).filter(
        ListeningHistory.user_id == current_user.user_id
    ).scalar() or 0

    # Actividad por hora
    hourly_data = db.query(
        ListeningHistory.hour_of_day.label("h"),
        func.count(ListeningHistory.id).label("v")
    ).filter(ListeningHistory.user_id == current_user.user_id)\
     .group_by(ListeningHistory.hour_of_day)\
     .order_by(ListeningHistory.hour_of_day).all()

    # Actividad por día de la semana
    weekly_data = db.query(
        ListeningHistory.day_of_week.label("d"),
        func.count(ListeningHistory.id).label("v")
    ).filter(ListeningHistory.user_id == current_user.user_id)\
     .group_by(ListeningHistory.day_of_week).all()

    # Géneros más escuchados (Ponderado por reproducciones)
    from app.db.models import Artist
    genre_data = db.query(Artist.genres, Artist.name).join(
        ListeningHistory, Artist.artist_id == ListeningHistory.artist_id
    ).filter(ListeningHistory.user_id == current_user.user_id).all()
    
    genre_mapping = {
        # Vallenato & Tropical
        "silvestre dangond": ["vallenato", "latino"],
        "patricia teherán": ["vallenato", "latino"],
        "otto serge": ["vallenato", "latino"],
        "peter manjarrés": ["vallenato", "latino"],
        "binomio de oro de américa": ["vallenato", "latino"],
        "los diablitos": ["vallenato", "latino"],
        
        # Urbano & Reggaeton
        "j balvin": ["reggaetón", "urbano"],
        "paulo londo": ["trap", "urbano"],
        "paulo londra": ["trap", "urbano"],
        "sebastian yatra": ["pop latino", "reggaetón"],
        "piso 21": ["pop latino", "reggaetón"],
        "luister la voz": ["champedance", "reggaetón"],
        
        # Pop & Balada
        "morat": ["pop latino", "indie pop"],
        "fonseca": ["pop latino", "tropipop"],
        "miley cyrus": ["pop", "dance pop"],
        "kany garcía": ["pop", "balada"],
        "benson boone": ["pop", "indie pop"],
        "ed sheeran": ["pop", "acoustic"],
        "teddy swims": ["soul", "pop"],
        "alex warren": ["pop", "indie pop"],
        
        # Rock
        "queen": ["rock", "classic rock"],
        "ac/dc": ["hard rock", "rock"],
        "scorpions": ["hard rock", "classic rock"],
        
        # Bandas sonoras, épica & clásica
        "gabriel saban": ["soundtrack", "classical"],
        "berend salverda": ["soundtrack", "ambient"],
        "samuel kim": ["epic score", "soundtrack"],
        "eternal eclipse": ["epic score", "soundtrack"],
        "rok nardin": ["epic score", "soundtrack"],
        "hidden citizens": ["epic score", "soundtrack"]
    }

    all_genres = {}
    for g_list, artist_name in genre_data:
        genres = []
        if g_list:
            genres = g_list
        else:
            name_lower = artist_name.lower().strip() if artist_name else ""
            genres = genre_mapping.get(name_lower, ["pop"])
            
        for g in genres:
            g_title = g.title()
            all_genres[g_title] = all_genres.get(g_title, 0) + 1
    
    top_genres = sorted(all_genres.items(), key=lambda x: x[1], reverse=True)[:5]
    # Sumar las ocurrencias de los top 5 para calcular el porcentaje
    total_g = sum(dict(top_genres).values()) or 1

    # Rango de fechas
    date_range = db.query(
        func.min(ListeningHistory.played_at).label("min_d"),
        func.max(ListeningHistory.played_at).label("max_d")
    ).filter(ListeningHistory.user_id == current_user.user_id).first()

    # Map any day of week format (English names, Spanish names, numbers) to Spanish abbreviations
    days_map = {
        "Monday": "Lun", "Mon": "Lun", "0": "Lun", "lunes": "Lun", "Lunes": "Lun",
        "Tuesday": "Mar", "Tue": "Mar", "1": "Mar", "martes": "Mar", "Martes": "Mar",
        "Wednesday": "Mié", "Wed": "Mié", "2": "Mié", "miércoles": "Mié", "Miércoles": "Mié",
        "Thursday": "Jue", "Thu": "Jue", "3": "Jue", "jueves": "Jue", "Jueves": "Jue",
        "Friday": "Vie", "Fri": "Vie", "4": "Vie", "viernes": "Vie", "Viernes": "Vie",
        "Saturday": "Sáb", "Sat": "Sáb", "5": "Sáb", "sábado": "Sáb", "Sábado": "Sáb",
        "Sunday": "Dom", "Sun": "Dom", "6": "Dom", "domingo": "Dom", "Domingo": "Dom"
    }
    
    order_map = {"Lun": 0, "Mar": 1, "Mié": 2, "Jue": 3, "Vie": 4, "Sáb": 5, "Dom": 6}
    
    weekly_list = []
    # Deduplicate weekly data in case of mixed database values
    dedup = {}
    for r in weekly_data:
        day_label = days_map.get(r.d, r.d[:3] if r.d else "Lun")
        dedup[day_label] = dedup.get(day_label, 0) + r.v
    
    for day, val in dedup.items():
        weekly_list.append({"d": day, "v": val})
        
    weekly_list.sort(key=lambda x: order_map.get(x["d"], 7))

    return {
        "total_plays": total_plays,
        "total_artists": total_artists,
        "total_tracks": total_tracks,
        "hourly": [{"h": str(r.h).zfill(2), "v": r.v} for r in hourly_data],
        "weekly": weekly_list,
        "genres": [{"g": g, "v": int((v/total_g)*100)} for g, v in top_genres],
        "min_date": date_range.min_d.isoformat() if date_range and date_range.min_d else None,
        "max_date": date_range.max_d.isoformat() if date_range and date_range.max_d else None
    }
