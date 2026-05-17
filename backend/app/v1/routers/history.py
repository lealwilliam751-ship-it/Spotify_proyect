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
    genre_data = db.query(Artist.genres).join(
        ListeningHistory, Artist.artist_id == ListeningHistory.artist_id
    ).filter(ListeningHistory.user_id == current_user.user_id).all()
    
    all_genres = {}
    for g_list in genre_data:
        if g_list[0]:
            # Cada reproducción suma a los géneros del artista
            for g in g_list[0]:
                all_genres[g] = all_genres.get(g, 0) + 1
    
    top_genres = sorted(all_genres.items(), key=lambda x: x[1], reverse=True)[:5]
    # Sumar solo las ocurrencias de los top 5 para que el % sume 100 (o el total real)
    total_g = sum(all_genres.values()) or 1

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
        "hourly": [{"h": str(r.h).zfill(2), "v": r.v} for r in hourly_data],
        "weekly": weekly_list,
        "genres": [{"g": g, "v": int((v/total_g)*100)} for g, v in top_genres],
        "min_date": date_range.min_d.isoformat() if date_range and date_range.min_d else None,
        "max_date": date_range.max_d.isoformat() if date_range and date_range.max_d else None
    }
