"""
filename: security.py
description: Utilidades para el manejo de seguridad, incluyendo la generación y validación de tokens JWT.
"""

from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Genera un token JWT para el usuario."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Union[str, None]:
    """Verifica un token JWT y retorna el subject (user_id)."""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None
