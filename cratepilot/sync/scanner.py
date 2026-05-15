"""Initial library scanner."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from cratepilot.db.repositories.sync_event_repo import SyncEventRepository
from cratepilot.db.repositories.track_repo import TrackPayload, TrackRepository
from cratepilot.metadata.adapter import MetadataAdapter
from cratepilot.utils.hashing import sha256_file


SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".aiff", ".aif", ".m4a", ".aac"}


@dataclass
class ScanResult:
    scanned_files: int = 0
    imported_tracks: int = 0
    failed_files: int = 0


def run_initial_scan(root_folder: str, session_factory: sessionmaker) -> ScanResult:
    adapter = MetadataAdapter()
    result = ScanResult()
    root = Path(root_folder).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Root folder does not exist: {root}")

    with session_factory() as session:
        track_repo = TrackRepository(session)
        event_repo = SyncEventRepository(session)
        seen_paths: set[str] = set()
        for file_path in root.rglob("*"):
            if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            result.scanned_files += 1
            seen_paths.add(str(file_path))
            try:
                stat = file_path.stat()
                tags = adapter.read_tags(str(file_path))
                track = track_repo.upsert_track(
                    TrackPayload(
                        absolute_path=str(file_path),
                        file_name=file_path.name,
                        extension=file_path.suffix.lower().lstrip("."),
                        file_size_bytes=stat.st_size,
                        mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                        sha256=sha256_file(str(file_path)),
                        duration_sec=tags.duration_sec,
                        title=tags.title,
                        artist=tags.artist,
                        album=tags.album,
                        year=tags.year,
                        genre=tags.genre,
                        bpm=tags.bpm,
                        musical_key=tags.musical_key,
                        comment=tags.comment,
                        track_number=tags.track_number,
                        tag_version=tags.tag_version,
                    )
                )
                event_repo.append_event(track.id, "created", "success", {"path": str(file_path)})
                result.imported_tracks += 1
            except Exception as exc:
                result.failed_files += 1
                event_repo.append_event(None, "created", "failed", {"path": str(file_path)}, error_message=str(exc))
        track_repo.set_missing_if_not_seen(seen_paths)
        session.commit()
    return result
