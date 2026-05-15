import os

import psycopg
import pytest


REQUIRED_DB_ENV_VARS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")


@pytest.fixture(scope="session")
def db_connection():
    missing = [key for key in REQUIRED_DB_ENV_VARS if not os.getenv(key)]
    if missing:
        pytest.skip(
            "Database CRUD tests require env vars: "
            + ", ".join(REQUIRED_DB_ENV_VARS)
            + f". Missing: {', '.join(missing)}"
        )

    conn = psycopg.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        autocommit=False,
    )
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def db_cursor(db_connection):
    with db_connection.cursor() as cursor:
        try:
            yield cursor
        finally:
            db_connection.rollback()
