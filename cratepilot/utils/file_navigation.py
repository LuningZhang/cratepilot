"""File navigation helpers for macOS."""

from pathlib import Path
import subprocess


def reveal_in_finder(path: str) -> None:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    subprocess.run(["open", "-R", path], check=True)
