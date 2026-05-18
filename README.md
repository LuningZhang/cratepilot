# CratePilot

CratePilot is a macOS desktop app for managing a local DJ music library with PostgreSQL as the source of truth and metadata/tag sync back to files.

## What it does
1. Scans a local root folder and ingests MP3/WAV/FLAC/AIFF/M4A/AAC into PostgreSQL.
2. Lets you search tracks, edit metadata, bulk edit selected tracks, and detect duplicates.
3. Writes metadata updates back to file tags immediately.
4. Optionally renames the audio filename when changing title (user-controlled in edit dialog).
5. Reveals selected tracks in Finder.
6. Supports conflict/reconcile actions and optional live folder watching.

## Prerequisites
1. **macOS 13+** (Finder integration uses `open -R`).
2. **Python 3.10+**.
3. **PostgreSQL 14+** running locally.
4. Terminal tools: `git`.

### macOS PostgreSQL quick start (Homebrew)
1. `brew install postgresql@16`
2. `brew services start postgresql@16`
3. Verify server is reachable: `psql -d postgres -c "SELECT version();"`

## Setup from a fresh clone
1. Clone and enter the repo:
   `git clone <your-repo-url> && cd stat_project`
2. Create and activate a virtual environment:
   `python3 -m venv .venv && source .venv/bin/activate`
3. Install dependencies:
   `pip install -e '.[dev]'`
4. Create local environment config:
   `cp .env.example .env`
5. Edit `.env` for your PostgreSQL instance:
   - `DB_DSN` should point to your target app DB (example: `postgresql://<db_user>:<db_password>@localhost:5432/cratepilot`)
   - `DB_ADMIN_DSN` should point to an admin DB that can create `DB_NAME` (usually `postgres`)
   - `DB_NAME` defaults to `cratepilot`
   - `ROOT_FOLDER` is your music library root path
6. Start the app:
   `cratepilot`

On startup, CratePilot automatically creates `DB_NAME` if needed and applies all SQL migrations in `db/migrations/`.

## Environment variables
| Variable | Required | Purpose |
| --- | --- | --- |
| `DB_DSN` | Yes | App database connection string. |
| `DB_ADMIN_DSN` | Yes | Admin connection string used to create `DB_NAME` if missing. |
| `DB_NAME` | Yes | Database name to create/use. |
| `ROOT_FOLDER` | Yes | Root folder containing local audio files. |
| `DB_HOST` | No | Optional; only for `tests/integration/test_songs_crud.py`. |
| `DB_PORT` | No | Optional; only for `tests/integration/test_songs_crud.py`. |
| `DB_USER` | No | Optional; only for `tests/integration/test_songs_crud.py`. |
| `DB_PASSWORD` | No | Optional; only for `tests/integration/test_songs_crud.py`. |

## Database and schema
1. Version-controlled schema artifacts are in `db/migrations/*.sql` and `db/schema.dbml`.
2. `db/seeds/sample_tracks.sql` contains synthetic sample data for manual testing.
3. Local runtime DB files are not committed (PostgreSQL is external to this repo).

## Development commands
1. Run app: `cratepilot`
2. Run tests: `pytest -q`

## Known limitations
1. **macOS-only UX assumptions**: Finder reveal is implemented with `open -R`; Linux/Windows are not supported.
2. **Single-library scope**: one local root folder at a time; no multi-root library management yet.
3. **No cloud/remote sync**: this is local-machine only; no multi-device conflict resolution.
4. **No Serato integration yet**: CratePilot does not import/export Serato crates in V1.
5. **Watcher behavior**: live watcher is session-based and must be started from the UI each launch.
6. **Integration CRUD test scope**: `tests/integration/test_songs_crud.py` targets a `songs` table fixture schema, not the app’s `tracks` table.
