"""Application configuration scaffolding."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    db_dsn: str
    root_folder: str
    macos_min_version: str = "13.0"


def load_settings() -> Settings:
    return Settings(
        db_dsn=os.getenv("DB_DSN", "postgresql://localhost:5432/cratepilot"),
        root_folder=os.getenv("ROOT_FOLDER", ""),
    )
