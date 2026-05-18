from pathlib import Path

import pytest

from cratepilot.utils.file_navigation import reveal_in_finder


def test_reveal_in_finder_raises_for_missing_path(tmp_path):
    missing = tmp_path / "missing.mp3"
    with pytest.raises(FileNotFoundError):
        reveal_in_finder(str(missing))


def test_reveal_in_finder_runs_open(monkeypatch, tmp_path):
    target = tmp_path / "track.mp3"
    target.write_bytes(b"x")
    called = {}

    def _fake_run(cmd, check):
        called["cmd"] = cmd
        called["check"] = check

    monkeypatch.setattr("cratepilot.utils.file_navigation.subprocess.run", _fake_run)
    reveal_in_finder(str(target))
    assert called["cmd"] == ["open", "-R", str(target)]
    assert called["check"] is True
