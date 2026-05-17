"""
filename: spotify_client.py
author: Antigravity AI
date: 2026-05-10
version: 1.0
description: Cliente HTTP reutilizable para interactuar con la Web API de Spotify.
"""

import httpx
from app.core.config import settings

class SpotifyClient:
    """Cliente para realizar peticiones autenticadas a Spotify."""
    
    BASE_URL = "https://api.spotify.com/v1"
    
    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        # Connection pooling and persistent keep-alive sessions
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0),
            headers=self.headers
        )

    async def get(self, endpoint: str, params: dict = None):
        """Realiza una petición GET a un endpoint específico de Spotify con timeout."""
        url = f"{self.BASE_URL}{endpoint}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Cierra el cliente HTTP persistente."""
        await self.client.aclose()

    @staticmethod
    def get_auth_url(client_id: str, redirect_uri: str, scope: str, state: str, code_challenge: str):
        """Genera la URL de autorización para el flujo PKCE."""
        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge_method": "S256",
            "code_challenge": code_challenge
        }
        query_params = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.spotify.com/authorize?{query_params}"
