"""
filename: schemas.py
description: Schemas Pydantic para la serialización de datos del DWH.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: int
    spotify_id: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    country: Optional[str] = None
    followers: Optional[int] = None
    product: Optional[str] = None

    class Config:
        from_attributes = True


class ArtistSchema(BaseModel):
    artist_id: int
    spotify_id: str
    name: str
    popularity: Optional[int] = None
    followers_count: Optional[int] = None
    genres: Optional[List[str]] = None

    class Config:
        from_attributes = True


class TrackSchema(BaseModel):
    track_id: int
    spotify_id: str
    name: str
    artist_id: Optional[int] = None
    album_name: Optional[str] = None
    duration_ms: Optional[int] = None
    popularity: Optional[int] = None
    explicit: Optional[bool] = None

    class Config:
        from_attributes = True


class ListeningHistorySchema(BaseModel):
    id: int
    user_id: int
    track_id: int
    artist_id: int
    played_at: datetime
    hour_of_day: Optional[int] = None
    day_of_week: Optional[str] = None
    context_type: Optional[str] = None

    class Config:
        from_attributes = True


class ETLAuditSchema(BaseModel):
    audit_id: int
    spotify_user_id: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    users_new: Optional[int] = 0
    artists_new: Optional[int] = 0
    tracks_new: Optional[int] = 0
    history_new: Optional[int] = 0

    class Config:
        from_attributes = True
