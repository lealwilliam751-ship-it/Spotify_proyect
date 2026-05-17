"""
filename: etl.py
description: Router para la orquestación y consulta del estado del pipeline ETL.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, ETLAudit
from app.v1.deps import get_current_user
from app.v1.services.etl_service import ETLService

router = APIRouter()

@router.post("/run")
async def run_etl(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Dispara la ejecución del pipeline ETL completo en segundo plano."""
    # Pasamos solo el ID para que el servicio sea totalmente independiente
    etl_service = ETLService(None, None) 
    background_tasks.add_task(etl_service.run_full_pipeline, current_user.user_id)
    return {"message": "Pipeline ETL iniciado en segundo plano"}

@router.get("/status")
async def get_etl_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna el historial de ejecuciones de la tabla etl_audit para el usuario actual."""
    history = db.query(ETLAudit).filter(
        ETLAudit.spotify_user_id == current_user.spotify_id
    ).order_by(ETLAudit.started_at.desc()).all()
    return history
