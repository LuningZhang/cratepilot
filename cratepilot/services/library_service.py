"""Library workflows for V1."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import sessionmaker

from cratepilot.db.repositories.edit_history_repo import EditHistoryRepository
from cratepilot.db.repositories.sync_event_repo import SyncEventRepository
from cratepilot.db.repositories.track_repo import EDITABLE_FIELDS, TrackRepository
from cratepilot.metadata.adapter import MetadataAdapter
from cratepilot.services.duplicates import detect_exact_duplicates, detect_fuzzy_duplicates
from cratepilot.services.file_name import unique_path_for_title


@dataclass
class BulkResult:
    success_count: int
    failed: list[str]


def _track_to_editable(track) -> dict[str, object]:
    return {field: getattr(track, field) for field in EDITABLE_FIELDS}


class LibraryService:
    """High-level service operations."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
        self.adapter = MetadataAdapter()

    def list_tracks(self, search: str = "") -> list:
        with self.session_factory() as session:
            return TrackRepository(session).list_tracks(search=search)

    def get_track(self, track_id):
        with self.session_factory() as session:
            return TrackRepository(session).get_track(track_id)

    def update_track_metadata(
        self,
        track_id,
        updates: dict[str, object],
        edited_by: str = "local_user",
        rename_file_with_title: bool = False,
    ) -> bool:
        with self.session_factory() as session:
            tracks = TrackRepository(session)
            events = SyncEventRepository(session)
            history = EditHistoryRepository(session)
            track = tracks.get_track(track_id)
            if track is None:
                return False
            clean_updates = {k: v for k, v in updates.items() if k in EDITABLE_FIELDS}
            renamed_from = None
            renamed_to = None
            try:
                self.adapter.write_tags(track.absolute_path, clean_updates)
                if rename_file_with_title and clean_updates.get("title"):
                    target_path = unique_path_for_title(track.absolute_path, str(clean_updates["title"]))
                    if str(target_path) != track.absolute_path:
                        renamed_from = track.absolute_path
                        renamed_to = str(target_path)
                        Path(track.absolute_path).rename(target_path)
                        tracks.update_file_path(track, str(target_path))
                changes = tracks.update_metadata_fields(track, clean_updates)
                if changes:
                    history.append_changes(track.id, changes, edited_by=edited_by)
                events.append_event(
                    track.id,
                    "manual_edit",
                    "success",
                    {
                        "fields": list(clean_updates.keys()),
                        "renamed_file": renamed_to is not None,
                        "new_path": renamed_to,
                    },
                )
                session.commit()
                return True
            except Exception as exc:
                session.rollback()
                if renamed_from and renamed_to and Path(renamed_to).exists() and not Path(renamed_from).exists():
                    try:
                        Path(renamed_to).rename(renamed_from)
                    except OSError:
                        pass
                track = tracks.get_track(track_id)
                if track is not None:
                    tracks.mark_error(track)
                events.append_event(
                    track_id,
                    "manual_edit",
                    "failed",
                    {"fields": list(clean_updates.keys()), "renamed_file": renamed_to is not None},
                    str(exc),
                )
                session.commit()
                return False

    def bulk_update_metadata(self, track_ids: list, updates: dict[str, object]) -> BulkResult:
        failed: list[str] = []
        success = 0
        for track_id in track_ids:
            ok = self.update_track_metadata(track_id, updates, edited_by="bulk")
            if ok:
                success += 1
            else:
                failed.append(str(track_id))
        return BulkResult(success_count=success, failed=failed)

    def reconcile_track(self, track_id) -> bool:
        with self.session_factory() as session:
            tracks = TrackRepository(session)
            events = SyncEventRepository(session)
            track = tracks.get_track(track_id)
            if track is None:
                return False
            try:
                file_tags = self.adapter.read_tags(track.absolute_path)
            except Exception as exc:
                tracks.mark_error(track)
                events.append_event(track.id, "reconcile", "failed", {"path": track.absolute_path}, str(exc))
                session.commit()
                return False
            db_values = _track_to_editable(track)
            file_values = {
                "title": file_tags.title,
                "artist": file_tags.artist,
                "album": file_tags.album,
                "year": file_tags.year,
                "genre": file_tags.genre,
                "bpm": file_tags.bpm,
                "musical_key": file_tags.musical_key,
                "comment": file_tags.comment,
                "track_number": file_tags.track_number,
            }
            diff = {key: {"db": db_values.get(key), "file": file_values.get(key)} for key in EDITABLE_FIELDS if db_values.get(key) != file_values.get(key)}
            if diff:
                tracks.mark_conflict(track)
                events.append_event(track.id, "reconcile", "success", {"conflict": diff})
            else:
                tracks.set_status_pending(track)
                tracks.update_metadata_fields(track, {})
                track.sync_status = "synced"
                track.last_tag_read_at = datetime.now(timezone.utc)
                events.append_event(track.id, "reconcile", "success", {"conflict": {}})
            session.commit()
            return True

    def resolve_conflict(self, track_id, mode: str, manual_updates: dict[str, object] | None = None) -> bool:
        with self.session_factory() as session:
            tracks = TrackRepository(session)
            events = SyncEventRepository(session)
            track = tracks.get_track(track_id)
            if track is None:
                return False
            try:
                if mode == "keep_db":
                    payload = _track_to_editable(track)
                    self.adapter.write_tags(track.absolute_path, payload)
                    tracks.update_metadata_fields(track, {})
                elif mode == "accept_file":
                    file_tags = self.adapter.read_tags(track.absolute_path)
                    payload = {
                        "title": file_tags.title,
                        "artist": file_tags.artist,
                        "album": file_tags.album,
                        "year": file_tags.year,
                        "genre": file_tags.genre,
                        "bpm": file_tags.bpm,
                        "musical_key": file_tags.musical_key,
                        "comment": file_tags.comment,
                        "track_number": file_tags.track_number,
                    }
                    tracks.update_metadata_fields(track, payload)
                else:
                    payload = manual_updates or {}
                    self.adapter.write_tags(track.absolute_path, payload)
                    tracks.update_metadata_fields(track, payload)
                track.sync_status = "synced"
                events.append_event(track.id, "conflict_resolve", "success", {"mode": mode})
                session.commit()
                return True
            except Exception as exc:
                tracks.mark_error(track)
                events.append_event(track.id, "conflict_resolve", "failed", {"mode": mode}, str(exc))
                session.commit()
                return False

    def list_conflicts(self) -> list:
        with self.session_factory() as session:
            return TrackRepository(session).list_conflicts()

    def find_duplicates(self) -> dict[str, object]:
        with self.session_factory() as session:
            tracks = TrackRepository(session).list_tracks(limit=5000)
        exact = detect_exact_duplicates(tracks)
        fuzzy = detect_fuzzy_duplicates(tracks)
        return {"exact_groups": exact, "fuzzy_candidates": fuzzy}
