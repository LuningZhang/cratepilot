"""Track repository."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from cratepilot.db.models import Track

EDITABLE_FIELDS = {
    "title",
    "artist",
    "album",
    "year",
    "genre",
    "bpm",
    "musical_key",
    "comment",
    "track_number",
}


@dataclass
class TrackPayload:
    absolute_path: str
    file_name: str
    extension: str
    file_size_bytes: int
    mtime: datetime
    sha256: Optional[str]
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
        return self.session.scalars(select(Track).where(Track.absolute_path == absolute_path)).first()

    def get_track(self, track_id) -> Optional[Track]:
        return self.session.scalars(select(Track).where(Track.id == track_id)).first()

    def get_tracks_by_ids(self, track_ids: list) -> list[Track]:
        if not track_ids:
            return []
        return list(self.session.scalars(select(Track).where(Track.id.in_(track_ids))))

    def list_tracks(self, search: str = "", limit: int = 5000) -> list[Track]:
        statement = select(Track)
        token = search.strip()
        if token:
            query = f"%{token}%"
            statement = statement.where(
                or_(
                    Track.title.ilike(query),
                    Track.artist.ilike(query),
                    Track.album.ilike(query),
                    Track.genre.ilike(query),
                    Track.absolute_path.ilike(query),
                )
            )
        statement = statement.order_by(Track.artist.asc().nulls_last(), Track.title.asc().nulls_last()).limit(limit)
        return list(self.session.scalars(statement))

    def list_conflicts(self) -> list[Track]:
        return list(self.session.scalars(select(Track).where(Track.sync_status == "conflict").order_by(Track.updated_at.desc())))

    def upsert_track(self, payload: TrackPayload) -> Track:
        track = self.find_by_path(payload.absolute_path)
        if track is None:
            track = Track(absolute_path=payload.absolute_path, file_name=payload.file_name, extension=payload.extension)
            self.session.add(track)
        track.file_name = payload.file_name
        track.extension = payload.extension
        track.file_size_bytes = payload.file_size_bytes
        track.mtime = payload.mtime
        track.sha256 = payload.sha256
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
        track.last_tag_read_at = datetime.now(timezone.utc)
        self.session.flush()
        return track

    def set_missing_if_not_seen(self, keep_paths: set[str]) -> int:
        changed = 0
        for track in self.session.scalars(select(Track)):
            if track.absolute_path not in keep_paths and track.sync_status != "missing":
                track.sync_status = "missing"
                track.missing_at = datetime.now(timezone.utc)
                changed += 1
        return changed

    def update_metadata_fields(self, track: Track, updates: dict[str, object]) -> dict[str, tuple[object, object]]:
        changes: dict[str, tuple[object, object]] = {}
        for field, new_value in updates.items():
            if field not in EDITABLE_FIELDS:
                continue
            old_value = getattr(track, field)
            if old_value != new_value:
                setattr(track, field, new_value)
                changes[field] = (old_value, new_value)
        if changes:
            track.sync_status = "synced"
            track.last_tag_write_at = datetime.now(timezone.utc)
            track.missing_at = None
        self.session.flush()
        return changes

    def update_file_path(self, track: Track, new_path: str) -> None:
        path_obj = Path(new_path)
        track.absolute_path = str(path_obj)
        track.file_name = path_obj.name
        track.extension = path_obj.suffix.lower().lstrip(".")
        track.missing_at = None
        self.session.flush()

    def mark_conflict(self, track: Track) -> None:
        track.sync_status = "conflict"
        self.session.flush()

    def mark_error(self, track: Track) -> None:
        track.sync_status = "error"
        self.session.flush()

    def set_status_pending(self, track: Track) -> None:
        track.sync_status = "pending"
        self.session.flush()
