"""
filename: spotify_service.py
description: Servicio para manejar la autenticación y comunicación con Spotify.
"""

import hashlib
import base64
import secrets
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import PKCESession, User

class SpotifyService:
    @staticmethod
    def generate_pkce_codes():
        """Genera el code_verifier y code_challenge para PKCE."""
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().replace("=", "")
        return code_verifier, code_challenge

    @staticmethod
    def create_pkce_session(db: Session, state: str, verifier: str):
        """Guarda la sesión PKCE en la base de datos."""
        session = PKCESession(state=state, verifier=verifier)
        db.add(session)
        db.commit()
        return session

    @staticmethod
    def get_pkce_session(db: Session, state: str):
        """Recupera la sesión PKCE por su state."""
        return db.query(PKCESession).filter(PKCESession.state == state).first()

    @staticmethod
    async def exchange_code_for_token(code: str, verifier: str):
        """Intercambia el código de autorización por tokens."""
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "code_verifier": verifier
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise Exception(f"Error al obtener token: {response.text}")
            return response.json()

    @staticmethod
    async def refresh_token(refresh_token: str):
        """Refresca el access token de Spotify."""
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": settings.SPOTIFY_CLIENT_ID
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                raise Exception(f"Error al refrescar token: {response.text}")
            return response.json()
