"""
filename: session.py
author: Antigravity AI
date: 2026-05-10
version: 1.0
description: Configuración del motor de SQLAlchemy y generador de sesiones para la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Crear el motor de la base de datos
engine = create_engine(settings.DATABASE_URL)

# Crear el generador de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Generador de sesión de base de datos para usar como dependencia en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
