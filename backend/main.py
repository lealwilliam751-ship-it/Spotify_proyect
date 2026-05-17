"""
filename: main.py
author: Antigravity AI
date: 2026-05-10
version: 1.0
description: Punto de entrada principal para la API de Spotify DWH. Configura la aplicación FastAPI y los middlewares.
"""

# Force IPv4 resolution to prevent broken IPv6 system/network routing from causing ConnectTimeout errors in Python
import socket
orig_getaddrinfo = socket.getaddrinfo
def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if family == socket.AF_UNSPEC or family == socket.AF_INET6:
        family = socket.AF_INET
    return orig_getaddrinfo(host, port, family, type, proto, flags)
socket.getaddrinfo = patched_getaddrinfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.v1.api import router as v1_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para el Data Warehouse personal de Spotify"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de las rutas de la versión 1
app.include_router(v1_router, prefix="/v1")

@app.get("/")
async def root():
    """Ruta raíz para verificar que la API está funcionando."""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
