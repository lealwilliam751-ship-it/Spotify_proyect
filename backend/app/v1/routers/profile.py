"""
filename: profile.py
description: Router para obtener información del perfil del usuario almacenada en el DWH.
"""

from fastapi import APIRouter, Depends
from app.db.models import User
from app.v1.deps import get_current_user
from app.v1.schemas import UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retorna el perfil del usuario actual desde la dimensión dim_users."""
    return current_user
