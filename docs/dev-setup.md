# Developer Setup (macOS only)

## 1. Prerequisites
1. macOS 13+.
2. Python 3.12+.
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
1. Create database `cratepilot`.
2. Run SQL migrations in order from `db/migrations/`.
3. Optional: load sample data from `db/seeds/sample_tracks.sql`.

## 4. Tests
1. Run unit and integration skeleton tests with `pytest`.

## 5. Local folder setup
1. Point `ROOT_FOLDER` to a small test music directory.
2. Use fixture audio files in `tests/fixtures/sample_audio/` as they are added.
