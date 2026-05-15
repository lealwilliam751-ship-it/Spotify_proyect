"""
filename: tracks.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Router de tracks - obtiene datos de canciones desde Spotify.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models import DimUser
from app.services.spotify_service import get_recently_played

router = APIRouter()

@router.get("/recent")
def get_recent_tracks_endpoint(
    current_user: DimUser = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=50)
):
    """
    Obtiene las canciones recientemente escuchadas por el usuario autenticado desde Spotify.
    
    Requiere token de acceso válido de Spotify almacenado en dim_users.
    """
    if not current_user.spotify_access_token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no valid Spotify access token. Please re-authenticate."
        )
    
    try:
        items = get_recently_played(
            access_token=current_user.spotify_access_token,
            limit=limit
        )
        
        # Formatear respuesta limpia
        formatted_tracks = []
        for item in items:
            track = item["track"]
            played_at = item["played_at"]
            
            formatted_tracks.append({
                "track_id": track["id"],
                "name": track["name"],
                "duration_ms": track["duration_ms"],
                "explicit": track["explicit"],
                "album_name": track["album"]["name"],
                "album_images": track["album"].get("images", []),
                "artists": [
                    {
                        "id": artist["id"],
                        "name": artist["name"]
                    }
                    for artist in track["artists"]
                ],
                "played_at": played_at
            })
        
        return {
            "count": len(formatted_tracks),
            "tracks": formatted_tracks
        }
        
    except Exception as e:
        from fastapi import HTTPException, status
        error_msg = str(e)
        if "expired" in error_msg.lower() or "invalid" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Spotify token expired. Please re-authenticate via /v1/auth/login"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error fetching data from Spotify: {error_msg}"
            )