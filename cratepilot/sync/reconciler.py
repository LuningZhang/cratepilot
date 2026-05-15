"""Periodic reconciliation workflows."""

from sqlalchemy.orm import sessionmaker

from cratepilot.db.repositories.track_repo import TrackRepository
from cratepilot.services.library_service import LibraryService


def run_reconciliation(session_factory: sessionmaker) -> tuple[int, int]:
    service = LibraryService(session_factory)
    with session_factory() as session:
        tracks = TrackRepository(session).list_tracks(limit=10000)
    processed = 0
    conflicted = 0
    for track in tracks:
        ok = service.reconcile_track(track.id)
        if ok:
            processed += 1
    conflicts = service.list_conflicts()
    conflicted = len(conflicts)
    return processed, conflicted
