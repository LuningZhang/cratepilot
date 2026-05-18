# Developer Setup (macOS only)

## 1. Prerequisites
1. macOS 13+.
2. Python 3.10+.
3. One PostgreSQL option:
   - Postgres.app (recommended for local desktop use)
   - Homebrew PostgreSQL
   - Docker PostgreSQL container

## 2. Environment
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -e .[dev]`
3. Copy `.env.example` to `.env` and update values.

## 3. Database bootstrap
1. Set `DB_DSN`, `DB_NAME`, and `DB_ADMIN_DSN` in `.env`.
2. App startup auto-creates `DB_NAME` if missing.
3. App startup auto-applies all SQL files in `db/migrations/` in lexical order.
4. Optional: manually load `db/seeds/sample_tracks.sql`.

## 4. Tests
1. Run tests with `pytest`.

## 5. Local folder setup
1. Point `ROOT_FOLDER` to a small test music directory.
2. Use fixture audio files in `tests/fixtures/sample_audio/` as they are added.

## 6. Launch
1. `cratepilot`
2. Click **Scan Library**.
3. Optional: start live monitoring with **Start Watcher**.
4. Use the top-right **sun/moon** button to toggle light/dark theme.
