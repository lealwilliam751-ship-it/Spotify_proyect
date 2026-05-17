"""
filename: artists.py
description: Router para consultar los artistas almacenados en la dimensión dim_artists.
"""

from typing import List
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from sqlalchemy import func
from app.db.models import User, Artist, ListeningHistory
from app.v1.deps import get_current_user

router = APIRouter()

@router.get("/top")
async def get_top_artists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna los artistas más escuchados basados en el historial."""
    results = db.query(
        Artist.name,
        Artist.spotify_id,
        func.count(ListeningHistory.id).label("play_count")
    ).join(ListeningHistory, Artist.artist_id == ListeningHistory.artist_id)\
     .filter(ListeningHistory.user_id == current_user.user_id)\
     .group_by(Artist.artist_id)\
     .order_by(func.count(ListeningHistory.id).desc())\
     .limit(5).all()
    
    return [{"name": r.name, "spotify_id": r.spotify_id, "play_count": r.play_count} for r in results]
