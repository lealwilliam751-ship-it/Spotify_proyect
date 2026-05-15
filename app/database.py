"""
filename: database.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Configuración de conexión a base de datos y dependencia de sesión.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()