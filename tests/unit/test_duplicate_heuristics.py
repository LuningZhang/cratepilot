from datetime import datetime, timezone
from decimal import Decimal
import uuid

from cratepilot.db.models import Track
from cratepilot.services.duplicates import detect_fuzzy_duplicates


def _track(track_id: str, title: str, artist: str, duration: Decimal):
    track = Track(
        id=uuid.UUID(track_id),
        absolute_path=f"/tmp/{track_id}.mp3",
        file_name=f"{track_id}.mp3",
        extension="mp3",
        file_size_bytes=1,
        mtime=datetime.now(timezone.utc),
    )
    track.title = title
    track.artist = artist
    track.duration_sec = duration
    return track


def test_detect_fuzzy_duplicates():
    left = _track("11111111-1111-1111-1111-111111111111", "Song A", "Artist A", Decimal("120.0"))
    right = _track("22222222-2222-2222-2222-222222222222", "Song A", "Artist A", Decimal("121.0"))
    candidates = detect_fuzzy_duplicates([left, right])
    assert len(candidates) == 1
    assert candidates[0].score == 1.0
