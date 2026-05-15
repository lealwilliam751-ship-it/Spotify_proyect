"""
filename: main.py
author: Santiago Capacho
date: 2026-05-14
version: 1.0
description: Punto de entrada principal de la aplicación FastAPI.
"""
PCKE_SESSIONS= {}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.v1.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(api_router, prefix="/v1")

@app.get("/")
def read_root():
    return {"message": "Spotify DWH API is running"}