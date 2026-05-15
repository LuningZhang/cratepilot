"""Filename helpers for title-based renaming."""

import re
from pathlib import Path

INVALID_CHARS = re.compile(r"[\\/:*?\"<>|]+")


def title_to_stem(title: str) -> str:
    cleaned = INVALID_CHARS.sub("_", title).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned[:120] if cleaned else "untitled"


def unique_path_for_title(current_path: str, title: str) -> Path:
    original = Path(current_path)
    stem = title_to_stem(title)
    candidate = original.with_name(f"{stem}{original.suffix}")
    if candidate == original:
        return candidate
    index = 1
    while candidate.exists():
        candidate = original.with_name(f"{stem} ({index}){original.suffix}")
        index += 1
    return candidate
