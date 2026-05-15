"""File navigation helpers for macOS."""

import subprocess


def reveal_in_finder(path: str) -> None:
    subprocess.run(["open", "-R", path], check=True)
