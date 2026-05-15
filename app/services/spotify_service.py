"""
filename: spotify_service.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Servicios para interactuar con la API de Spotify.
"""
import httpx
from app.core.config import settings
from app.models import DimUser
from datetime import timedelta
from sqlalchemy.orm import Session

def get_spotify_headers(access_token: str) -> dict:
    """Devuelve headers necesarios para llamadas a Spotify API."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

def get_top_artists(access_token: str, limit: int = 20, time_range: str = "medium_term") -> list:
    url = "https://api.spotify.com/v1/me/top/artists"
    params = {
        "limit": min(limit, 50),
        "time_range": time_range
    }
    
    headers = get_spotify_headers(access_token)
    response = httpx.get(url, headers=headers, params=params)
    
    if response.status_code == 401:
        raise Exception("Spotify access token expired or invalid. Please re-authenticate.")
    elif response.status_code != 200:
        raise Exception(f"Spotify API error: {response.status_code} - {response.text[:200]}")
    
    data = response.json()
    return data.get("items", [])


def get_recently_played(access_token: str, limit: int = 50, refresh_token: str = None, db: Session = None, user: DimUser = None) -> list:
    """
    Obtiene canciones recientes. Si el token expira, intenta renovarlo automáticamente.
    """
    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {"limit": min(limit, 50)}
    headers = get_spotify_headers(access_token)
    
    response = httpx.get(url, headers=headers, params=params)
    
    # Si el token expiró (401) y tenemos refresh_token, intentamos renovar
    if response.status_code == 401 and refresh_token and db and user:
        try:
            new_tokens = refresh_spotify_token(refresh_token)
            update_user_tokens_in_db(db, user, new_tokens)
            
            # Reintentar la llamada con el nuevo token
            headers = get_spotify_headers(new_tokens["access_token"])
            response = httpx.get(url, headers=headers, params=params)
            
        except Exception as e:
            raise Exception(f"Token refresh failed: {str(e)}. Please re-authenticate.")
            
    if response.status_code == 401:
        raise Exception("Spotify access token expired and no refresh token available. Please re-authenticate.")
    elif response.status_code != 200:
        raise Exception(f"Spotify API error: {response.status_code} - {response.text[:200]}")
    
    data = response.json()
    return data.get("items", [])



def refresh_spotify_token(refresh_token: str) -> dict:
    """
    Renueva el access_token de Spotify usando el refresh_token.
    
    Args:
        refresh_token: Token de refresco guardado en la BD
        
    Returns:
        Diccionario con el nuevo access_token y expires_in
    """
    url = "https://accounts.spotify.com/api/token"
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID
        # Nota: Algunos clientes requieren client_secret, pero PKCE puro a veces no.
        # Si falla, agrega: "client_secret": settings.SPOTIFY_CLIENT_SECRET
    }
    
    response = httpx.post(url, data=data)
    response.raise_for_status()
    return response.json()

def update_user_tokens_in_db(db: Session, user: DimUser, new_tokens: dict) -> None:
    """Actualiza los tokens del usuario en la BD después de un refresh."""
    user.spotify_access_token = new_tokens["access_token"]
    # Spotify a veces no devuelve un nuevo refresh_token, usamos el anterior si no viene
    if "refresh_token" in new_tokens:
        user.spotify_refresh_token = new_tokens["refresh_token"]
        
    user.token_expires_at = datetime.utcnow() + timedelta(seconds=new_tokens["expires_in"])
    db.commit()
    db.refresh(user)