"""
filename: auth.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Router de autenticación con Spotify usando PKCE.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import secrets
import hashlib
import base64
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.auth_service import handle_spotify_callback
from app.database import get_db  # <-- Necesitamos esta dependencia
from app.core.pkce_store import PKCE_SESSIONS, cleanup_expired_pkce_sessions
router = APIRouter()


# Endpoint de login: genera código PKCE y redirige a Spotify
@router.get("/login")
def login(request: Request):
    cleanup_expired_pkce_sessions()  # Limpia estados viejos antes de crear uno nuevo

    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')

    state = secrets.token_urlsafe(32)
    
    # Guardar session temporalmente en app.state (como antes)
    PKCE_SESSIONS[state] = {
        "verifier": code_verifier,
        "created_at": datetime.utcnow()
    }

    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-read-private user-read-email user-top-read user-read-recently-played",
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge
    }

    spotify_auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return RedirectResponse(url=spotify_auth_url)

# Endpoint de callback: recibe el código de Spotify y devuelve JWT
@router.get("/callback")
def callback(request: Request, code: str, state: str, db: Session = Depends(get_db)):
    # Verificar que el state exista y sea válido
    if state not in PKCE_SESSIONS:
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")

    session_data = PKCE_SESSIONS.pop(state)
    code_verifier = session_data["verifier"]
    

    try:
        # Llamar al servicio que hace todo el trabajo
        result = handle_spotify_callback(db, code, state, code_verifier)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during authentication: {str(e)}")