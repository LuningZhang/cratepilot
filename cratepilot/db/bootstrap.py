"""Database bootstrap for local MVP."""

from pathlib import Path

import psycopg
from psycopg import sql
from sqlalchemy import text

from cratepilot.config import Settings
from cratepilot.db.connection import make_engine


def ensure_database_exists(settings: Settings) -> None:
    with psycopg.connect(settings.db_admin_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (settings.db_name,))
            if cur.fetchone() is None:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.db_name)))


def apply_migrations(settings: Settings, migrations_dir: Path) -> None:
    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        return
    with psycopg.connect(settings.db_dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            for migration in migration_files:
                cur.execute(migration.read_text())


def initialize_database(settings: Settings, migrations_dir: Path) -> None:
    ensure_database_exists(settings)
    apply_migrations(settings, migrations_dir)
    engine = make_engine(settings.db_dsn)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
