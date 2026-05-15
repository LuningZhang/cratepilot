"""Metadata data structures."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ParsedTags:
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
