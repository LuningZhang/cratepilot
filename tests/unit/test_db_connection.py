from cratepilot.db.connection import _sqlalchemy_dsn


def test_sqlalchemy_dsn_uses_psycopg_driver():
    assert _sqlalchemy_dsn("postgresql://localhost:5432/cratepilot") == "postgresql+psycopg://localhost:5432/cratepilot"
    assert _sqlalchemy_dsn("postgres://localhost:5432/cratepilot") == "postgresql+psycopg://localhost:5432/cratepilot"
    assert _sqlalchemy_dsn("postgresql+psycopg://localhost:5432/cratepilot") == "postgresql+psycopg://localhost:5432/cratepilot"
