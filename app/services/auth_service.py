"""
filename: auth_service.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Servicios de autenticación con Spotify PKCE.
"""
from datetime import datetime
from app.models import PkceSession
from sqlalchemy.orm import Session

def create_pkce_session(state: str, verifier: str) -> PkceSession:
    """Crea una nueva sesión PKCE para almacenar el state y verifier."""
    return PkceSession(
        state=state,
        verifier=verifier,
        created_at=datetime.utcnow()
    )

def store_pkce_session(db: Session, session: PkceSession) -> None:
    """Guarda la sesión PKCE en la base de datos."""
    db.add(session)
    db.commit()
    db.refresh(session)