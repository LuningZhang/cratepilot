"""Sync event repository."""

from datetime import datetime, timezone
import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class SyncEventRepository:
    """Persistence operations for sync events."""

    def __init__(self, session: Session):
        self.session = session

    def append_event(self, track_id, event_type: str, status: str, payload: dict[str, Any] | None = None) -> None:
        data = payload or {}
        self.session.execute(
            text(
                """
                INSERT INTO sync_events (track_id, event_type, status, payload, created_at)
                VALUES (:track_id, :event_type, :status, CAST(:payload AS jsonb), :created_at)
                """
            ),
            {
                "track_id": track_id,
                "event_type": event_type,
                "status": status,
                "payload": json.dumps(data),
                "created_at": datetime.now(timezone.utc),
            },
        )
