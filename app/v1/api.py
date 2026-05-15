"""
filename: api.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Router principal que agrupa todos los endpoints de la API v1.
"""
from fastapi import APIRouter
from app.v1.routers import auth, profile, artists, tracks, history, etl

api_router = APIRouter()

# Cada router con su propio prefijo para mantener consistencia
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile"])
api_router.include_router(artists.router, prefix="/artists", tags=["Artists"])
api_router.include_router(tracks.router, prefix="/tracks", tags=["Tracks"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(etl.router, prefix="/etl", tags=["ETL"])