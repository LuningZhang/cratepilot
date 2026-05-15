import pytest

from cratepilot.sync.scanner import run_initial_scan


def test_scan_raises_for_missing_folder():
    with pytest.raises(FileNotFoundError):
        run_initial_scan("/definitely/missing/path", None)  # type: ignore[arg-type]
