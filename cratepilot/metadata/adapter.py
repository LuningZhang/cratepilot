"""Mutagen adapter."""

from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional

from mutagen import File as MutagenFile

from cratepilot.metadata.types import ParsedTags


def _first(values: Any) -> Optional[str]:
    if values is None:
        return None
    if isinstance(values, list):
        return str(values[0]) if values else None
    return str(values)


def _parse_int(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    token = value.split("/")[0].strip()
    if token.isdigit():
        return int(token)
    digits = "".join(ch for ch in token if ch.isdigit())
    if len(digits) >= 4:
        return int(digits[:4])
    return None


def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    if not value:
        return None
    try:
        return Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return None


class MetadataAdapter:
    """Reads metadata from supported audio files."""

    def read_tags(self, path: str) -> ParsedTags:
        audio = MutagenFile(path, easy=True)
        detailed_audio = MutagenFile(path)
        if audio is None or detailed_audio is None:
            raise ValueError(f"Unsupported or unreadable audio file: {path}")

        tags = audio.tags or {}
        duration = getattr(getattr(detailed_audio, "info", None), "length", None)
        duration_sec = Decimal(str(round(duration, 3))) if duration else None
        return ParsedTags(
            duration_sec=duration_sec,
            title=_first(tags.get("title")),
            artist=_first(tags.get("artist")),
            album=_first(tags.get("album")),
            year=_parse_int(_first(tags.get("date"))),
            genre=_first(tags.get("genre")),
            bpm=_parse_decimal(_first(tags.get("bpm"))),
            musical_key=_first(tags.get("initialkey")) or _first(tags.get("key")),
            comment=_first(tags.get("comment")),
            track_number=_first(tags.get("tracknumber")),
            tag_version=Path(path).suffix.lower().lstrip("."),
        )
