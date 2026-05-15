"""Database connection helpers."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def _sqlalchemy_dsn(db_dsn: str) -> str:
    if db_dsn.startswith("postgresql+"):
        return db_dsn
    if db_dsn.startswith("postgresql://"):
        return db_dsn.replace("postgresql://", "postgresql+psycopg://", 1)
    if db_dsn.startswith("postgres://"):
        return db_dsn.replace("postgres://", "postgresql+psycopg://", 1)
    return db_dsn


def make_engine(db_dsn: str) -> Engine:
    return create_engine(_sqlalchemy_dsn(db_dsn), future=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
