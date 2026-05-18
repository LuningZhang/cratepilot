"""Onboarding prompts for required local settings."""

from pathlib import Path

from dotenv import set_key
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox, QWidget

from cratepilot.config import APP_ENV_PATH, Settings


def _write_env_value(key: str, value: str) -> None:
    APP_ENV_PATH.touch(exist_ok=True)
    set_key(str(APP_ENV_PATH), key, value)


def _read_runtime_setting(settings: QSettings, key: str) -> str:
    value = settings.value(key, "")
    if value is None:
        return ""
    return str(value).strip()


def ensure_runtime_settings(parent: QWidget, settings: Settings) -> Settings:
    runtime_settings = QSettings("CratePilot", "CratePilot")
    db_dsn = settings.db_dsn
    db_name = settings.db_name
    db_admin_dsn = settings.db_admin_dsn
    root_folder = settings.root_folder

    if not root_folder:
        root_folder = _read_runtime_setting(runtime_settings, "runtime/root_folder")
    if root_folder and not Path(root_folder).expanduser().exists():
        root_folder = ""

    if not root_folder:
        chosen = QFileDialog.getExistingDirectory(parent, "Select your DJ root music folder")
        if not chosen:
            raise RuntimeError("Root folder is required.")
        root_folder = chosen
        _write_env_value("ROOT_FOLDER", root_folder)

    if not db_dsn:
        db_dsn = _read_runtime_setting(runtime_settings, "runtime/db_dsn")
    if not db_dsn:
        value, ok = QInputDialog.getText(parent, "Database DSN", "Enter DB_DSN:")
        if not ok or not value.strip():
            raise RuntimeError("DB_DSN is required.")
        db_dsn = value.strip()
        _write_env_value("DB_DSN", db_dsn)

    if not db_name:
        db_name = _read_runtime_setting(runtime_settings, "runtime/db_name")
    if not db_name:
        value, ok = QInputDialog.getText(parent, "Database name", "Enter DB_NAME:", text="cratepilot")
        if not ok or not value.strip():
            raise RuntimeError("DB_NAME is required.")
        db_name = value.strip()
        _write_env_value("DB_NAME", db_name)

    if not db_admin_dsn:
        db_admin_dsn = _read_runtime_setting(runtime_settings, "runtime/db_admin_dsn")
    if not db_admin_dsn:
        value, ok = QInputDialog.getText(parent, "Admin DSN", "Enter DB_ADMIN_DSN:")
        if not ok or not value.strip():
            raise RuntimeError("DB_ADMIN_DSN is required.")
        db_admin_dsn = value.strip()
        _write_env_value("DB_ADMIN_DSN", db_admin_dsn)

    path = Path(root_folder).expanduser()
    if not path.exists():
        QMessageBox.critical(parent, "Invalid folder", f"Root folder does not exist:\n{path}")
        raise RuntimeError("Invalid root folder.")

    runtime_settings.setValue("runtime/root_folder", str(path))
    runtime_settings.setValue("runtime/db_dsn", db_dsn)
    runtime_settings.setValue("runtime/db_name", db_name)
    runtime_settings.setValue("runtime/db_admin_dsn", db_admin_dsn)

    return Settings(
        db_dsn=db_dsn,
        db_name=db_name,
        db_admin_dsn=db_admin_dsn,
        root_folder=str(path),
        macos_min_version=settings.macos_min_version,
    )
