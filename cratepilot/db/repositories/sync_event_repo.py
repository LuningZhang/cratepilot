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

    def append_event(
        self,
        track_id,
        event_type: str,
        status: str,
        payload: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        data = payload or {}
        self.session.execute(
            text(
                """
                INSERT INTO sync_events (track_id, event_type, status, error_message, payload, created_at)
                VALUES (:track_id, :event_type, :status, :error_message, CAST(:payload AS jsonb), :created_at)
                """
            ),
            {
                "track_id": track_id,
                "event_type": event_type,
                "status": status,
                "error_message": error_message,
                "payload": json.dumps(data),
                "created_at": datetime.now(timezone.utc),
            },
        )

    def recent_events(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                SELECT event_type, status, error_message, payload::text, created_at
                FROM sync_events
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [
            {
                "event_type": row[0],
                "status": row[1],
                "error_message": row[2],
                "payload": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]
