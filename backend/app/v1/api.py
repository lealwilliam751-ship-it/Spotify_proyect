"""
filename: api.py
author: Antigravity AI
date: 2026-05-10
version: 1.0
description: Agrupador de routers para la versión 1 de la API.
"""

from fastapi import APIRouter
from app.v1.routers import auth, profile, artists, tracks, history, etl

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(profile.router, prefix="/profile", tags=["Profile"])
router.include_router(artists.router, prefix="/artists", tags=["Artists"])
router.include_router(tracks.router, prefix="/tracks", tags=["Tracks"])
router.include_router(history.router, prefix="/history", tags=["History"])
router.include_router(etl.router, prefix="/etl", tags=["ETL"])
