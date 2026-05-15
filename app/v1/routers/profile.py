"""
filename: profile.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Router de perfil de usuario.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models import DimUser

router = APIRouter()

@router.get("/me")
def get_profile(current_user: DimUser = Depends(get_current_user)):
    """Devuelve los datos del usuario autenticado."""
    return {
        "user_id": current_user.user_id,
        "spotify_id": current_user.spotify_id,
        "display_name": current_user.display_name,
        "email": current_user.email,
        "country": current_user.country,
        "followers": current_user.followers,
        "product": current_user.product,
        "loaded_at": current_user.loaded_at
    }