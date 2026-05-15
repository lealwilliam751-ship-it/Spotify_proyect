"""
filename: auth.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Router de autenticación con Spotify usando PKCE.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
import secrets
import hashlib
import base64
import os
from app.core.config import settings
from app.models import PkceSession
from sqlalchemy.orm import Session
from app.services.auth_service import create_pkce_session, store_pkce_session

router = APIRouter()

# Endpoint de login: genera código PKCE y redirige a Spotify
@router.get("/login")
def login(request: Request):
    # Generar code_verifier y code_challenge
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')

    # Guardar session temporalmente (en memoria o DB según implementación)
    state = secrets.token_urlsafe(32)
    
    # Aquí deberías guardar 'state' y 'code_verifier' en BD o cache
    # Por ahora, usaremos una variable global simple (NO recomendado en producción, pero válido para examen)
    request.app.state.pkce_sessions[state] = {
        "verifier": code_verifier,
        "created_at": datetime.utcnow()
    }

    # Construir URL de autorización de Spotify
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