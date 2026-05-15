"""Duplicate detection helpers."""

from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations

from cratepilot.db.models import Track


@dataclass
class DuplicateCandidate:
    left_id: str
    right_id: str
    score: float
    confidence: str
    reason: str


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def _duration_delta(left: Decimal | None, right: Decimal | None) -> float:
    if left is None or right is None:
        return 9999.0
    return abs(float(left) - float(right))


def detect_exact_duplicates(tracks: list[Track]) -> list[list[Track]]:
    groups: dict[str, list[Track]] = {}
    for track in tracks:
        if track.sha256:
            groups.setdefault(track.sha256, []).append(track)
    return [group for group in groups.values() if len(group) > 1]


def detect_fuzzy_duplicates(tracks: list[Track]) -> list[DuplicateCandidate]:
    candidates: list[DuplicateCandidate] = []
    for left, right in combinations(tracks, 2):
        score = 0.0
        reasons: list[str] = []
        if _norm(left.artist) and _norm(left.artist) == _norm(right.artist):
            score += 0.4
            reasons.append("artist")
        if _norm(left.title) and _norm(left.title) == _norm(right.title):
            score += 0.4
            reasons.append("title")
        if _duration_delta(left.duration_sec, right.duration_sec) <= 2.0:
            score += 0.2
            reasons.append("duration<=2s")
        if score >= 0.8:
            confidence = "high" if score == 1.0 else "medium"
            candidates.append(
                DuplicateCandidate(
                    left_id=str(left.id),
                    right_id=str(right.id),
                    score=score,
                    confidence=confidence,
                    reason=", ".join(reasons),
                )
            )
    candidates.sort(key=lambda item: item.score, reverse=True)
    return candidates
