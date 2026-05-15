"""Periodic reconciliation placeholder for MVP."""

from pathlib import Path


def run_reconciliation(root_folder: str) -> int:
    root = Path(root_folder).expanduser()
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())
