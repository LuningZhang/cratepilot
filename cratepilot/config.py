"""Application configuration."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


APP_ENV_PATH = Path(".env")


@dataclass(frozen=True)
class Settings:
    db_dsn: str
    root_folder: str
    db_name: str
    db_admin_dsn: str
    macos_min_version: str = "13.0"


def load_settings() -> Settings:
    load_dotenv(APP_ENV_PATH)
    db_dsn = os.getenv("DB_DSN", "postgresql://localhost:5432/cratepilot")
    db_name = os.getenv("DB_NAME", "cratepilot")
    db_admin_dsn = os.getenv("DB_ADMIN_DSN", "postgresql://localhost:5432/postgres")
    root_folder = os.getenv("ROOT_FOLDER", "")
    return Settings(
        db_dsn=db_dsn,
        root_folder=root_folder,
        db_name=db_name,
        db_admin_dsn=db_admin_dsn,
    )
