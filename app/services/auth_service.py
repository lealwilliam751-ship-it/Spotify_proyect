"""
filename: auth_service.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Servicios de autenticación con Spotify PKCE y gestión de tokens.
"""
import httpx
from datetime import datetime, timedelta
from jose import jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import DimUser, PkceSession

def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    """Intercambia el código de autorización de Spotify por tokens."""
    token_url = "https://accounts.spotify.com/api/token"
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "code_verifier": code_verifier
    }
    
    # No se envía client_secret en PKCE puro según Spotify docs
    response = httpx.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

def get_or_create_user(db: Session, spotify_data: dict) -> DimUser:
    """Obtiene o crea un usuario en dim_users basado en datos de Spotify."""
    spotify_id = spotify_data["id"]
    user = db.query(DimUser).filter(DimUser.spotify_id == spotify_id).first()
    
    if not user:
        user = DimUser(
            spotify_id=spotify_id,
            display_name=spotify_data.get("display_name"),
            email=spotify_data.get("email"),
            country=spotify_data.get("country"),
            followers=spotify_data.get("followers", {}).get("total"),
            product=spotify_data.get("product")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def update_user_tokens(db: Session, user: DimUser, tokens: dict) -> None:
    """Actualiza los tokens del usuario en la BD."""
    user.spotify_access_token = tokens["access_token"]
    user.spotify_refresh_token = tokens.get("refresh_token", user.spotify_refresh_token)
    user.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
    db.commit()

def generate_jwt_token(user: DimUser) -> str:
    """Genera un JWT firmado para el frontend."""
    to_encode = {
        "sub": str(user.user_id),
        "spotify_id": user.spotify_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def handle_spotify_callback(db: Session, code: str, state: str, code_verifier: str) -> dict:
    """Procesa el callback de Spotify: obtiene tokens, guarda/actualiza usuario, genera JWT."""
    # 1. Intercambiar código por tokens
    tokens = exchange_code_for_tokens(code, code_verifier)
    
    # 2. Obtener perfil del usuario desde Spotify (necesario para email, etc.)
    profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile_response = httpx.get(profile_url, headers=headers)
    profile_response.raise_for_status()
    spotify_profile = profile_response.json()
    
    # 3. Guardar o actualizar usuario en BD
    user = get_or_create_user(db, spotify_profile)
    update_user_tokens(db, user, tokens)
    
    # 4. Generar JWT para el frontend
    access_token = generate_jwt_token(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "spotify_id": user.spotify_id
    }