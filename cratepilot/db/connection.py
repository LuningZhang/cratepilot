"""Database connection scaffolding."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cratepilot.config import load_settings


def make_engine():
    settings = load_settings()
    return create_engine(settings.db_dsn, future=True)


def make_session_factory():
    return sessionmaker(bind=make_engine(), autoflush=False, autocommit=False, future=True)
