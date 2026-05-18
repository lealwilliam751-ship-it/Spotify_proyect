"""
filename: auth.py
description: Router para la autenticación con Spotify mediante flujo OAuth PKCE.
El ETL se dispara automáticamente como BackgroundTask al completar el login.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.spotify_client import SpotifyClient
from app.core.security import create_access_token
from app.db.session import get_db, SessionLocal
from app.db.models import User
from app.v1.services.spotify_service import SpotifyService
from app.v1.services.etl_service import ETLService

router = APIRouter()


def _run_etl_sync(user_id: int):
    """
    Función sincrónica que abre su propia sesión de DB y ejecuta el ETL.
    Se llama desde BackgroundTasks (que NO soporta async directamente).
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            print(f"ETL BACKGROUND: usuario {user_id} no encontrado")
            return
        print(f"ETL BACKGROUND: iniciando pipeline para {user.spotify_id}")
        asyncio.run(ETLService(db, user).run_full_pipeline(user.user_id))
        print(f"ETL BACKGROUND: pipeline completado para {user.spotify_id}")
    except Exception as e:
        print(f"ETL BACKGROUND ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


@router.get("/login")
async def login(db: Session = Depends(get_db)):
    """Genera PKCE y redirige al usuario a la página de autorización de Spotify."""
    state = str(uuid.uuid4())
    verifier, challenge = SpotifyService.generate_pkce_codes()

    SpotifyService.create_pkce_session(db, state, verifier)

    scope = "user-read-private user-read-email user-top-read user-read-recently-played"
    auth_url = SpotifyClient.get_auth_url(
        client_id=settings.SPOTIFY_CLIENT_ID,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope=scope,
        state=state,
        code_challenge=challenge
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Callback que recibe el código de Spotify, emite el JWT y dispara el ETL."""
    try:
        # 1. Verificar state y obtener verifier
        pkce_session = SpotifyService.get_pkce_session(db, state)
        if not pkce_session:
            print(f"DEBUG ERROR: State {state} not found in database")
            raise HTTPException(status_code=400, detail="Estado inválido o sesión expirada")

        # 2. Intercambiar código por token
        try:
            tokens = await SpotifyService.exchange_code_for_token(code, pkce_session.verifier)
        except Exception as e:
            print(f"DEBUG ERROR Exchange Token: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error en Spotify: {str(e)}")

        # 3. Obtener perfil del usuario en Spotify
        client = SpotifyClient(tokens["access_token"])
        try:
            spotify_user = await client.get("/me")
        except Exception as e:
            error_detail = str(e)
            if hasattr(e, "response"):
                error_detail = f"{e.response.status_code}: {e.response.text}"
            print(f"DEBUG ERROR Get Profile: {error_detail}")
            raise HTTPException(status_code=500, detail=f"Spotify dijo: {error_detail}")

        # 4. Crear o actualizar usuario en la DB
        user = db.query(User).filter(User.spotify_id == spotify_user["id"]).first()
        if not user:
            user = User(spotify_id=spotify_user["id"])
            db.add(user)

        user.display_name = spotify_user.get("display_name")
        user.email = spotify_user.get("email")
        user.country = spotify_user.get("country")
        user.followers = spotify_user.get("followers", {}).get("total", 0)
        user.product = spotify_user.get("product")
        user.spotify_access_token = tokens["access_token"]
        user.spotify_refresh_token = tokens.get("refresh_token")
        user.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])

        db.commit()
        db.refresh(user)

        # 5. Eliminar sesión PKCE usada
        db.delete(pkce_session)
        db.commit()

        # 6. Generar JWT de la aplicación
        app_token = create_access_token(subject=user.user_id)

        # 7. Disparar el ETL en segundo plano (no bloquea la redirección)
        print(f"AUTH: scheduling background ETL for user_id={user.user_id}")
        background_tasks.add_task(_run_etl_sync, user.user_id)

        # 8. Redirigir al frontend
        frontend_url = f"{settings.FRONTEND_URL}/?access_token={app_token}"
        return RedirectResponse(url=frontend_url)

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"CRITICAL ERROR in auth callback: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
