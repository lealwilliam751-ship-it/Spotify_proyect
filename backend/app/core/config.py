from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr
from pathlib import Path
from dotenv import load_dotenv
import os
import sys

# Localizar la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = os.path.join(str(BASE_DIR), ".env")

# CARGA MANUAL FORZADA
if os.path.exists(ENV_FILE):
    load_dotenv(dotenv_path=ENV_FILE, override=True)
else:
    print(f"CRITICAL: .env file NOT FOUND at {ENV_FILE}", file=sys.stderr)

class Settings(BaseSettings):
    """Clase de configuración con carga forzada."""
    
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_if_env_fails")
    
    APP_NAME: str = os.getenv("APP_NAME", "Spotify DWH API")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    model_config = SettingsConfigDict(extra="ignore")

settings = Settings()

# Verificación de seguridad
if not settings.SPOTIFY_CLIENT_ID:
    print("WARNING: SPOTIFY_CLIENT_ID is empty after loading Settings!", file=sys.stderr)
