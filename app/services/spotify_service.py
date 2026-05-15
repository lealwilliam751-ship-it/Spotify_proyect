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


def get_recently_played(access_token: str, limit: int = 50) -> list:
    """
    Obtiene las canciones recientemente escuchadas por el usuario desde Spotify API.
    
    Args:
        access_token: Token de acceso de Spotify
        limit: Número de tracks a devolver (máx 50)
    
    Returns:
        Lista de diccionarios con datos de tracks recientes
    """
    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {
        "limit": min(limit, 50)  # Spotify limita a 50
    }
    
    headers = get_spotify_headers(access_token)
    response = httpx.get(url, headers=headers, params=params)
    
    if response.status_code == 401:
        raise Exception("Spotify access token expired or invalid. Please re-authenticate.")
    elif response.status_code != 200:
        raise Exception(f"Spotify API error: {response.status_code} - {response.text[:200]}")
    
    data = response.json()
    return data.get("items", [])