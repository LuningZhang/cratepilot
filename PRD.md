# PRD: Local DJ Library Manager

## 1. Product overview

### Working name
**CratePilot (v1)**

### Problem
Serato Pro library management is limited for direct local-file workflows. DJ libraries can reach gigabytes of files across folders, and metadata curation is hard when file tags and app/library records drift out of sync.

### Vision
A desktop app that manages a local music folder as a source collection, stores searchable metadata in PostgreSQL, and keeps database values and audio file tags synchronized in near real time.

### v1 product stance (confirmed)
- Desktop GUI app
- Local PostgreSQL as system of record
- Standalone library management (no direct Serato integration)
- Database edits auto-write back to file tags immediately

## 2. Goals and non-goals

### Goals
1. Index all supported songs under one root folder (including subfolders).
2. Detect new/changed/deleted files and sync metadata into PostgreSQL.
3. Parse and write tags for common DJ formats (MP3, WAV, FLAC, AIFF, M4A/AAC).
4. Provide fast GUI search/filter/sort/edit workflows.
5. Keep metadata bi-directionally consistent between DB and file tags.

### Non-goals (v1)
1. Full Serato crate/library sync.
2. Cloud sync / multi-device collaboration.
3. Audio analysis (BPM/key detection from waveform) beyond tag ingestion.
4. DRM-protected file support.

## 3. User personas and core jobs

### Primary persona
Independent DJ with a large local music library and regular new downloads.

### Core jobs
1. Import and monitor a root folder.
2. Find tracks quickly by artist/title/year/genre/comment/path.
3. Correct metadata in bulk.
4. Trust that edits persist both in app DB and actual file tags.

## 4. Research summary: implementation possibilities

## 4.1 Metadata read/write layer
- **Mutagen (recommended)**: Mature Python metadata library supporting MP3/FLAC/MP4/Ogg/WAV/AIFF with ID3/APEv2 handling.
- **Alternatives**: `eyed3` (MP3-focused), `tinytag` (primarily read use cases).
- **Decision**: Use **Mutagen** for broad format coverage and reliable write APIs.

## 4.2 File-system monitoring
- **watchdog (recommended)**: Cross-platform event watchers for create/modify/move/delete.
- **Alternative**: Periodic polling only (simpler but less responsive).
- **Decision**: Hybrid model: watchdog events + scheduled reconciliation scan.

## 4.3 Metadata enrichment (optional v1.5)
- **MusicBrainz API via `musicbrainzngs`** for lookup/normalization candidates.
- **Decision**: Keep enrichment as optional/manual workflow in v1 (avoid noisy auto-overwrites).

## 4.4 Desktop GUI options
- **PySide6 (recommended)**: Native desktop UX, mature table/form widgets, Python-first workflow.
- **Alternatives**: Flet (fast iteration), Electron/Tauri (higher web-stack overhead).
- **Decision**: **PySide6** for robust desktop data-grid interactions.

## 4.5 Database/search options
- **PostgreSQL (confirmed)** for local structured metadata and audit trail.
- Use standard btree indexes + optional full-text search (`tsvector`) for title/artist/comment discovery.

## 5. Product scope and requirements

## 5.1 Functional requirements
1. User sets one root music folder at onboarding.
2. App recursively scans folder and ingests supported audio files.
3. Each file is represented by one canonical DB row (unique by normalized absolute path + hash guard).
4. Tag parser extracts metadata fields into DB columns.
5. Filesystem events trigger incremental sync jobs.
6. In-app metadata edits update DB and immediately write to file tags.
7. If tag write fails, DB transaction is rolled back and user sees explicit error.
8. Bulk edit supported for selected tracks.
9. Search/filter by title, artist, album, year, genre, BPM, key, comments, extension, folder.
10. Duplicate detection by acoustic-agnostic heuristics (file hash + duration + title/artist similarity).
11. Show sync status per track: `synced`, `pending`, `error`, `conflict`.
12. Deletion handling:
   - File removed from disk -> mark row `missing` (soft-delete) with timestamp.
   - Optional hard-delete cleanup command.

## 5.2 Non-functional requirements
1. Local-first, offline-capable operation.
2. Indexing target: 50k tracks without UI lockups (background workers).
3. Search response target: <300 ms for common filtered queries on indexed fields.
4. Safe writes: no silent metadata loss; every write failure surfaced.
5. Cross-platform support priority: macOS first, then Windows.

## 6. Proposed architecture (v1)

## 6.1 Components
1. **Desktop GUI (PySide6)**: library table, detail panel, bulk edit controls, sync/error center.
2. **Sync service (Python worker)**: scan jobs, event handling, reconciliation, retries.
3. **Metadata adapter (Mutagen)**: read/write tag abstraction across formats.
4. **PostgreSQL layer**: core entities, indexes, audit logs, job state.
5. **Watcher layer (watchdog)**: listens to file events and enqueues sync tasks.

## 6.2 Data flow
1. Initial scan -> parse tags -> upsert tracks.
2. New file event -> parse and insert.
3. File modify event -> compare digest/mtime -> re-parse + upsert.
4. User edit in GUI -> DB update -> immediate tag write -> status update.
5. If external tag change happens -> watcher + reconciliation updates DB.

## 6.3 Source-of-truth rule
PostgreSQL is authoritative for app workflows; file tag writes happen immediately after DB change in the same logical operation. On failure, operation is marked failed and surfaced (no silent divergence).

## 7. Data model (initial)

## 7.1 `tracks`
- `id` (uuid, pk)
- `absolute_path` (text, unique)
- `file_name` (text)
- `extension` (text)
- `file_size_bytes` (bigint)
- `mtime` (timestamp)
- `sha256` (text, nullable during initial ingest)
- `duration_sec` (numeric)
- `title` (text)
- `artist` (text)
- `album` (text)
- `year` (int)
- `genre` (text)
- `bpm` (numeric)
- `musical_key` (text)
- `comment` (text)
- `track_number` (text)
- `tag_version` (text)
- `sync_status` (text)
- `last_tag_read_at` (timestamp)
- `last_tag_write_at` (timestamp)
- `created_at`, `updated_at` (timestamp)

## 7.2 `sync_events`
- `id` (uuid, pk)
- `track_id` (uuid, fk)
- `event_type` (created|modified|deleted|manual_edit|reconcile)
- `status` (success|failed)
- `error_message` (text)
- `created_at` (timestamp)

## 7.3 `edit_history`
- `id` (uuid, pk)
- `track_id` (uuid, fk)
- `field_name` (text)
- `old_value` (text)
- `new_value` (text)
- `edited_by` (text default `local_user`)
- `created_at` (timestamp)

## 7.4 Index strategy
- Unique index on `absolute_path`
- Btree indexes on `artist`, `title`, `year`, `genre`, `bpm`, `musical_key`
- Optional GIN index on `to_tsvector('simple', coalesce(title,'') || ' ' || coalesce(artist,'') || ' ' || coalesce(comment,''))`

## 8. UX requirements

1. **Library table view** with sortable columns and saved filters.
2. **Track detail panel** for single-item edits.
3. **Bulk edit modal** for multi-track changes.
4. **Sync activity panel** with retry action for failures.
5. **Conflict indicator** when disk metadata changes during active session.
6. **Dangerous operations** (bulk overwrite) require confirmation.

## 9. Error handling and edge cases

1. Unsupported/corrupt file -> mark row `error`, retain path and diagnostic.
2. Missing tag frames -> allow null fields; do not infer silently.
3. Read-only files or permission errors -> explicit write error with retry/help.
4. Rename/move operations -> detect via path + file signature where possible.
5. Duplicate paths from symlink loops -> skip and log.

## 10. Security and privacy

1. All data remains local by default.
2. No cloud upload in v1.
3. Optional enrichment API calls are opt-in and documented.

## 11. Delivery roadmap

## Milestone 1: Foundation
1. Project scaffold, config, DB schema, root-folder onboarding.
2. Initial recursive scanner with metadata extraction.
3. Basic table UI and track detail view.

## Milestone 2: Sync engine
1. Watchdog file-event ingestion.
2. Incremental upsert and deletion handling.
3. Edit-to-tag immediate write with transactional safeguards.

## Milestone 3: Power workflow
1. Bulk edit, advanced filters, error/retry dashboard.
2. Duplicate finder and quality checks.
3. Packaging for local desktop install.

## 12. Git and repo control (for GitHub upload)

1. Initialize git repository at project root.
2. Commit PRD as first baseline commit.
3. Use branch workflow:
   - `main`: stable releases
   - `feat/*`: feature work
   - `fix/*`: bug fixes
4. Keep `.env`, local DB dumps, and large audio files ignored via `.gitignore`.

## 13. Open questions for implementation phase

1. Preferred packaging target for desktop release (macOS app bundle vs script-run app).
2. Whether to include cue points/custom DJ fields in v1 schema.
3. Maximum expected library size (for worker/concurrency tuning).
