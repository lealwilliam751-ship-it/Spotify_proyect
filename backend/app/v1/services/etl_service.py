from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import User, Artist, Track, ListeningHistory, ETLAudit
from app.core.spotify_client import SpotifyClient
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

class ETLService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.spotify = SpotifyClient(user.spotify_access_token) if user else None
        self.audit = None
        self.errors = []

    async def run_full_pipeline(self, user_id: int):
        from app.db.session import SessionLocal
        db = SessionLocal()
        self.db = db
        self.user = db.query(User).filter(User.user_id == user_id).first()
        if not self.user:
            db.close(); return

        self.spotify = SpotifyClient(self.user.spotify_access_token)
        start_time = datetime.utcnow()
        
        try:
            self.audit = ETLAudit(spotify_user_id=self.user.spotify_id, started_at=start_time, status="RUNNING")
            self.db.add(self.audit)
            self.db.commit()

            await self._process_user_profile()
            await self._process_top_artists()
            await self._process_top_tracks()
            await self._process_listening_history()

            self.audit.status = "COMPLETED"
        except Exception as e:
            print(f"ETL ERROR: {e}")
            import traceback
            traceback.print_exc()
            if self.audit:
                self.audit.status = "FAILED"
                self.audit.error_message = str(e)[:500]
        finally:
            if self.audit:
                self.audit.finished_at = datetime.utcnow()
                self.audit.duration_ms = int((self.audit.finished_at - start_time).total_seconds() * 1000)
                self.db.commit()
            if hasattr(self, "spotify"):
                await self.spotify.close()
            self.db.close()

    async def _process_user_profile(self):
        data = await self.spotify.get("/me")
        self.user.display_name = data.get("display_name")
        self.db.commit()

    async def _process_top_artists(self):
        data = await self.spotify.get("/me/top/artists", params={"limit": 20})
        for item in data.get("items", []):
            stmt = insert(Artist).values(
                spotify_id=item["id"], name=item["name"], 
                genres=item.get("genres", []), popularity=item.get("popularity", 0)
            ).on_conflict_do_update(
                index_elements=["spotify_id"], 
                set_={"genres": item.get("genres", []), "popularity": item.get("popularity", 0)}
            )
            self.db.execute(stmt)
        self.db.commit()

    async def _process_top_tracks(self):
        data = await self.spotify.get("/me/top/tracks", params={"limit": 20})
        for item in data.get("items", []):
            artist = self.db.query(Artist).filter(Artist.spotify_id == item["artists"][0]["id"]).first()
            if not artist: continue
            stmt = insert(Track).values(
                spotify_id=item["id"], name=item["name"], artist_id=artist.artist_id,
                album_name=item["album"]["name"], popularity=item.get("popularity", 0)
            ).on_conflict_do_update(index_elements=["spotify_id"], set_={"popularity": item.get("popularity", 0)})
            self.db.execute(stmt)
        self.db.commit()

    async def _process_listening_history(self):
        # 1. Buscar la fecha de la última reproducción guardada
        last_play = self.db.query(func.max(ListeningHistory.played_at)).filter(
            ListeningHistory.user_id == self.user.user_id
        ).scalar()

        params = {"limit": 50}
        if last_play:
            from datetime import timezone
            # last_play is in UTC (naive), force timezone.utc to avoid system timezone interpretation shift
            utc_last_play = last_play.replace(tzinfo=timezone.utc)
            params["after"] = int(utc_last_play.timestamp() * 1000)

        data = await self.spotify.get("/me/player/recently-played", params=params)
        new_count = 0
        new_artists = 0
        new_tracks = 0
        
        for item in data.get("items", []):
            t_data = item["track"]
            played_at_str = item["played_at"].replace("Z", "")
            played_at = datetime.fromisoformat(played_at_str)
            
            # Upsert Artista
            stmt_art = insert(Artist).values(
                spotify_id=t_data["artists"][0]["id"], name=t_data["artists"][0]["name"]
            ).on_conflict_do_nothing()
            res_art = self.db.execute(stmt_art)
            if res_art.rowcount > 0: new_artists += 1
            artist = self.db.query(Artist).filter(Artist.spotify_id == t_data["artists"][0]["id"]).first()
            
            # Upsert Track
            stmt_track = insert(Track).values(
                spotify_id=t_data["id"], name=t_data["name"], artist_id=artist.artist_id,
                album_name=t_data["album"]["name"], duration_ms=t_data.get("duration_ms", 210000),
                popularity=t_data.get("popularity", 70), explicit=t_data.get("explicit", False)
            ).on_conflict_do_nothing()
            res_track = self.db.execute(stmt_track)
            if res_track.rowcount > 0: new_tracks += 1
            track = self.db.query(Track).filter(Track.spotify_id == t_data["id"]).first()
            
            # Insert Historia (Doble verificación por si acaso)
            days_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            day_name = days_names[played_at.weekday()]
            
            stmt_hist = insert(ListeningHistory).values(
                user_id=self.user.user_id, track_id=track.track_id, artist_id=artist.artist_id,
                played_at=played_at, day_of_week=day_name, hour_of_day=played_at.hour
            ).on_conflict_do_nothing()
            res = self.db.execute(stmt_hist)
            if res.rowcount > 0: new_count += 1
            
        self.audit.history_new = new_count
        self.audit.artists_new = new_artists
        self.audit.tracks_new = new_tracks

        # Enrich empty genres only for artists present in the user's actual listening history (batch by 50)
        empty_artists = self.db.query(Artist).join(
            ListeningHistory, Artist.artist_id == ListeningHistory.artist_id
        ).filter(
            ListeningHistory.user_id == self.user.user_id,
            Artist.genres == []
        ).distinct().all()
        if empty_artists:
            for i in range(0, len(empty_artists), 50):
                batch = empty_artists[i:i+50]
                ids_str = ",".join([a.spotify_id for a in batch])
                try:
                    artists_data = await self.spotify.get("/artists", params={"ids": ids_str})
                    for item in artists_data.get("artists", []):
                        if item:
                            artist_in_db = next((x for x in batch if x.spotify_id == item["id"]), None)
                            if artist_in_db:
                                artist_in_db.genres = item.get("genres", [])
                except Exception as ex:
                    print(f"Error enriching artist genres: {ex}")

        self.db.commit()
