"""
filename: artists.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Router de artistas - obtiene datos de artistas desde Spotify.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models import DimUser
from app.services.spotify_service import get_top_artists

router = APIRouter()

@router.get("/top")
def get_top_artists_endpoint(
    current_user: DimUser = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=50),
    time_range: str = Query(default="medium_term", regex="^(short_term|medium_term|long_term)$")
):
    """
    Obtiene los artistas top del usuario autenticado desde Spotify.
    
    Requiere token de acceso válido de Spotify almacenado en dim_users.
    """
    if not current_user.spotify_access_token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no valid Spotify access token. Please re-authenticate."
        )
    
    try:
        artists = get_top_artists(
            access_token=current_user.spotify_access_token,
            limit=limit,
            time_range=time_range
        )
        
        # Formatear respuesta limpia
        formatted_artists = [
            {
                "id": artist.get("id"),
                "name": artist.get("name"),
                "popularity": artist.get("popularity", 0),          # ← VALOR POR DEFECTO
                "followers": artist.get("followers", {}).get("total", 0),  # ← ANIDADO CON DEFAULT
                "genres": artist.get("genres", []),
                "external_urls": artist.get("external_urls", {})
            }
            for artist in artists
        ]
        
        return {
            "count": len(formatted_artists),
            "time_range": time_range,
            "artists": formatted_artists
        }
        
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error fetching data from Spotify: {str(e)}"
        )