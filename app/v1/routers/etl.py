"""
filename: etl.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Router de procesos ETL para cargar datos de Spotify en el Data Warehouse.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models import DimUser
from app.services.etl_service import run_etl_process

router = APIRouter()

@router.post("/run")
def run_etl_endpoint(
    current_user: DimUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ejecuta el proceso ETL para cargar el historial de escucha reciente del usuario en el DWH.
    
    Requiere token de acceso válido de Spotify almacenado en dim_users.
    """
    if not current_user.spotify_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no valid Spotify access token. Please re-authenticate."
        )
    
    try:
        result = run_etl_process(db, current_user)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ETL process failed: {str(e)}"
        )