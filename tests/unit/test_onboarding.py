from pathlib import Path

from cratepilot.config import Settings
from cratepilot.gui import onboarding


class _FakeQSettings:
    def __init__(self, initial=None):
        self.values = dict(initial or {})

    def value(self, key, default=""):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value


def _base_settings(root_folder: str = "") -> Settings:
    return Settings(
        db_dsn="postgresql://localhost:5432/cratepilot",
        db_name="cratepilot",
        db_admin_dsn="postgresql://localhost:5432/postgres",
        root_folder=root_folder,
    )


def test_uses_persisted_root_folder_without_prompt(monkeypatch, tmp_path):
    fake_runtime = _FakeQSettings({"runtime/root_folder": str(tmp_path)})
    monkeypatch.setattr(onboarding, "QSettings", lambda *_args: fake_runtime)
    monkeypatch.setattr(
        onboarding.QFileDialog,
        "getExistingDirectory",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Folder picker should not open")),
    )

    resolved = onboarding.ensure_runtime_settings(None, _base_settings(root_folder=""))

    assert resolved.root_folder == str(tmp_path), "Expected runtime settings root folder to be reused."
    assert fake_runtime.values["runtime/root_folder"] == str(tmp_path)


def test_reprompts_when_persisted_root_folder_is_missing(monkeypatch, tmp_path):
    missing = str(Path(tmp_path) / "does-not-exist")
    chosen = str(tmp_path / "new-root")
    Path(chosen).mkdir()

    fake_runtime = _FakeQSettings({"runtime/root_folder": missing})
    monkeypatch.setattr(onboarding, "QSettings", lambda *_args: fake_runtime)
    monkeypatch.setattr(onboarding.QFileDialog, "getExistingDirectory", lambda *_args, **_kwargs: chosen)

    recorded_env_writes = []
    monkeypatch.setattr(onboarding, "_write_env_value", lambda key, value: recorded_env_writes.append((key, value)))

    resolved = onboarding.ensure_runtime_settings(None, _base_settings(root_folder=""))

    assert resolved.root_folder == chosen, "Expected onboarding to request a new root folder when saved one is invalid."
    assert ("ROOT_FOLDER", chosen) in recorded_env_writes
    assert fake_runtime.values["runtime/root_folder"] == chosen
