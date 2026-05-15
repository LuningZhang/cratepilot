"""Edit history repository."""

from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.orm import Session


class EditHistoryRepository:
    """Persistence operations for edit history records."""

    def __init__(self, session: Session):
        self.session = session

    def append_changes(self, track_id, changes: dict[str, tuple[object, object]], edited_by: str = "local_user") -> None:
        now = datetime.now(timezone.utc)
        for field, (old, new) in changes.items():
            self.session.execute(
                text(
                    """
                    INSERT INTO edit_history (track_id, field_name, old_value, new_value, edited_by, created_at)
                    VALUES (:track_id, :field_name, :old_value, :new_value, :edited_by, :created_at)
                    """
                ),
                {
                    "track_id": track_id,
                    "field_name": field,
                    "old_value": None if old is None else str(old),
                    "new_value": None if new is None else str(new),
                    "edited_by": edited_by,
                    "created_at": now,
                },
            )
