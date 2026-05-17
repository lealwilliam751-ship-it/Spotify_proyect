"""
filename: tracks.py
description: Router para consultar las canciones almacenadas en la dimensión dim_tracks.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from sqlalchemy import func
from app.db.models import User, Track, ListeningHistory, Artist
from app.v1.deps import get_current_user

router = APIRouter()

@router.get("/top")
async def get_top_tracks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna los tracks más escuchados basados en el historial."""
    results = db.query(
        Track.name,
        Track.spotify_id,
        Artist.name.label("artist_name"),
        func.count(ListeningHistory.id).label("play_count")
    ).join(ListeningHistory, Track.track_id == ListeningHistory.track_id)\
     .join(Artist, Track.artist_id == Artist.artist_id)\
     .filter(ListeningHistory.user_id == current_user.user_id)\
     .group_by(Track.track_id, Artist.artist_id)\
     .order_by(func.count(ListeningHistory.id).desc())\
     .limit(5).all()
    
    return [
        {"name": r.name, "spotify_id": r.spotify_id, "artist_name": r.artist_name, "play_count": r.play_count} 
        for r in results
    ]
