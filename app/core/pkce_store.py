"""
filename: pkce_store.py
author: Santiago Capacho
date: 2026-05-15
version: 1.0
description: Almacén temporal en memoria para sesiones PKCE (solo desarrollo).
"""
import time
from datetime import datetime

# Diccionario global para almacenar estados PKCE temporales
PKCE_SESSIONS = {}

def cleanup_expired_pkce_sessions(max_age_seconds=300):  # 5 minutos
    """Elimina estados expirados del almacén."""
    now = time.time()
    expired_states = [
        state for state, data in PKCE_SESSIONS.items()
        if now - data["created_at"].timestamp() > max_age_seconds
    ]
    for state in expired_states:
        del PKCE_SESSIONS[state]