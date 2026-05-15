# CratePilot

macOS-first local DJ library manager.

## Current status
V1 build is runnable and includes:
1. Onboarding for local root folder + DB settings.
2. Auto database creation and auto migration on startup.
3. Initial recursive ingest scan for MP3/WAV/FLAC/AIFF/M4A/AAC.
4. Modern dark minimal desktop UI (PySide6) with search/filter.
5. Single-track edit with immediate file tag writeback.
6. Bulk edit with explicit editable fields and per-track result handling.
7. Conflict detection + resolve actions (keep DB / accept file).
8. Duplicate detection summary (exact hash groups + fuzzy candidates).
9. Optional live folder watcher that triggers incremental resync.

## Run from a clean clone
1. `git clone <your-repo-url> && cd stat_project`
2. `python3 -m venv .venv && source .venv/bin/activate`
3. `pip install -e '.[dev]'`
4. `cp .env.example .env`
5. Ensure PostgreSQL is running locally and reachable by `DB_ADMIN_DSN` and `DB_DSN`.
6. `cratepilot`

On first launch, pick your music root folder when prompted. The app creates the `cratepilot` database if missing and applies migrations automatically.
