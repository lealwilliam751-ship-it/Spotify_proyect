"""
filename: models.py
author: Antigravity AI
date: 2026-05-10
version: 1.0
description: Definición de los modelos de SQLAlchemy para el Data Warehouse de Spotify.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BIGINT, ARRAY, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    """Modelo para la dimensión dim_users."""
    __tablename__ = "dim_users"
    __table_args__ = {"schema": "dwh"}

    user_id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255))
    email = Column(String(255))
    country = Column(String(10))
    followers = Column(Integer)
    product = Column(String(20))
    spotify_access_token = Column(Text)
    spotify_refresh_token = Column(Text)
    token_expires_at = Column(DateTime)
    loaded_at = Column(DateTime, server_default=func.now())

class Artist(Base):
    """Modelo para la dimensión dim_artists."""
    __tablename__ = "dim_artists"
    __table_args__ = {"schema": "dwh"}

    artist_id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    popularity = Column(Integer)
    followers_count = Column(Integer)
    genres = Column(ARRAY(Text))
    loaded_at = Column(DateTime, server_default=func.now())

class Track(Base):
    """Modelo para la dimensión dim_tracks."""
    __tablename__ = "dim_tracks"
    __table_args__ = {"schema": "dwh"}

    track_id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    artist_id = Column(Integer, ForeignKey("dwh.dim_artists.artist_id"))
    album_name = Column(String(255))
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    explicit = Column(Boolean)
    loaded_at = Column(DateTime, server_default=func.now())

class ListeningHistory(Base):
    """Modelo para la tabla de hechos fact_listening_history."""
    __tablename__ = "fact_listening_history"
    __table_args__ = (
        UniqueConstraint('user_id', 'played_at', name='uq_user_played_at'),
        {"schema": "dwh"}
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("dwh.dim_users.user_id"), nullable=False)
    track_id = Column(Integer, ForeignKey("dwh.dim_tracks.track_id"), nullable=False)
    artist_id = Column(Integer, ForeignKey("dwh.dim_artists.artist_id"), nullable=False)
    played_at = Column(DateTime, nullable=False)
    hour_of_day = Column(Integer)
    day_of_week = Column(String(10))
    context_type = Column(String(50))

class ETLAudit(Base):
    """Modelo para la tabla de auditoría etl_audit."""
    __tablename__ = "etl_audit"
    __table_args__ = {"schema": "dwh"}

    audit_id = Column(Integer, primary_key=True, index=True)
    spotify_user_id = Column(String(100), nullable=False)
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    duration_ms = Column(Integer)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    users_new = Column(Integer, default=0)
    artists_new = Column(Integer, default=0)
    artists_skipped = Column(Integer, default=0)
    tracks_new = Column(Integer, default=0)
    tracks_skipped = Column(Integer, default=0)
    history_new = Column(Integer, default=0)
    history_skipped = Column(Integer, default=0)
    cursor_after_ms = Column(BIGINT)
    cursor_next_ms = Column(BIGINT)

class PKCESession(Base):
    """Modelo para la tabla operacional pkce_sessions (en el schema public)."""
    __tablename__ = "pkce_sessions"
    
    state = Column(String(128), primary_key=True)
    verifier = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
