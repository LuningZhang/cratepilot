"""Track repository."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from cratepilot.db.models import Track


@dataclass
class TrackPayload:
    absolute_path: str
    file_name: str
    extension: str
    file_size_bytes: int
    mtime: datetime
    duration_sec: Optional[Decimal]
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    year: Optional[int]
    genre: Optional[str]
    bpm: Optional[Decimal]
    musical_key: Optional[str]
    comment: Optional[str]
    track_number: Optional[str]
    tag_version: Optional[str]


class TrackRepository:
    """Persistence operations for tracks."""

    def __init__(self, session: Session):
        self.session = session

    def find_by_path(self, absolute_path: str) -> Optional[Track]:
        statement = select(Track).where(Track.absolute_path == absolute_path)
        return self.session.scalars(statement).first()

    def upsert_track(self, payload: TrackPayload) -> Track:
        track = self.find_by_path(payload.absolute_path)
        if track is None:
            track = Track(
                absolute_path=payload.absolute_path,
                file_name=payload.file_name,
                extension=payload.extension,
                file_size_bytes=payload.file_size_bytes,
                mtime=payload.mtime,
                duration_sec=payload.duration_sec,
                title=payload.title,
                artist=payload.artist,
                album=payload.album,
                year=payload.year,
                genre=payload.genre,
                bpm=payload.bpm,
                musical_key=payload.musical_key,
                comment=payload.comment,
                track_number=payload.track_number,
                tag_version=payload.tag_version,
                sync_status="synced",
            )
            self.session.add(track)
        else:
            track.file_name = payload.file_name
            track.extension = payload.extension
            track.file_size_bytes = payload.file_size_bytes
            track.mtime = payload.mtime
            track.duration_sec = payload.duration_sec
            track.title = payload.title
            track.artist = payload.artist
            track.album = payload.album
            track.year = payload.year
            track.genre = payload.genre
            track.bpm = payload.bpm
            track.musical_key = payload.musical_key
            track.comment = payload.comment
            track.track_number = payload.track_number
            track.tag_version = payload.tag_version
            track.sync_status = "synced"
        self.session.flush()
        return track

    def list_tracks(self, limit: int = 1000) -> list[Track]:
        statement = select(Track).order_by(Track.artist.asc().nulls_last(), Track.title.asc().nulls_last()).limit(limit)
        return list(self.session.scalars(statement))

    def get_track(self, track_id) -> Optional[Track]:
        statement = select(Track).where(Track.id == track_id)
        return self.session.scalars(statement).first()
