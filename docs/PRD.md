# PRD: CratePilot (Local DJ Library Manager)

## 1. Product overview

### Problem
Serato Pro is not optimized for direct, large-scale local file management. DJs need a local-first tool that keeps metadata organized across both a searchable library database and real audio file tags.

### Vision
CratePilot is a macOS desktop app that indexes a root music folder, manages track metadata in PostgreSQL, and synchronizes edits to file tags immediately with explicit conflict handling.

### v1 scope (locked)
1. Desktop GUI app (macOS only).
2. Local PostgreSQL is system of record.
3. Standalone local-library management only (no direct Serato integration).
4. Metadata edits from app trigger immediate tag write.

### v1 non-goals
1. Direct Serato crate/library sync.
2. Cloud sync or multi-user collaboration.
3. Audio-signal analysis (key/BPM detection from waveform).

## 2. Target users and jobs

### Primary user
Independent DJ managing gigabytes of local files and frequent new downloads.

### Core jobs
1. Onboard a root music folder and PostgreSQL once.
2. Search/filter/sort tracks quickly.
3. Edit metadata in single or bulk flows.
4. Trust synchronization between DB rows and file tags.

## 3. Platform and environment

1. **Platform:** macOS only in v1.
2. **Minimum OS:** macOS 13 Ventura.
3. **Hardware:** Apple Silicon and Intel Macs supported.
4. **Runtime:** Python 3.12+.
5. **Distribution target (v1):** script-run developer build; packaged signed `.dmg` is post-v1.

## 4. Product decisions (from research)

1. **Tag I/O:** Mutagen.
2. **Filesystem watch:** watchdog + periodic reconciliation scan.
3. **GUI:** PySide6.
4. **Database:** PostgreSQL 16+ local instance.
5. **Optional enrichment (post-v1):** MusicBrainz lookup via `musicbrainzngs`.

## 5. Onboarding and setup requirements

### 5.1 First-run onboarding wizard
1. Choose PostgreSQL setup path:
   - Postgres.app
   - Homebrew service
   - Docker container
2. Enter or auto-detect DB connection values.
3. Validate connection and create database if absent.
4. Run migrations automatically.
5. Select root music folder.
6. Confirm initial scan start.

### 5.2 Failure handling in onboarding
1. If DB connection fails, show exact connection error and recovery hint.
2. If migration fails, block app entry and show next-step command.
3. If folder permission is denied, request a new folder path.

## 6. Functional requirements

1. Recursively scan root folder and ingest supported formats: MP3, FLAC, WAV, AIFF, M4A/AAC.
2. Maintain one canonical row per absolute path.
3. Parse tags into normalized DB columns.
4. Track create/modify/move/delete via watchdog events and reconciliation pass.
5. Support single-track metadata edit.
6. Support bulk edit with explicit editable-field matrix.
7. Auto-write tags immediately after edit request.
8. Surface per-track sync status and detailed errors.
9. Support duplicate detection in two tiers: exact duplicates and fuzzy candidates.
10. Keep full edit audit log with retention policy.

## 7. Synchronization model

### 7.1 Source of truth
PostgreSQL is authoritative for accepted app edits. External file changes never silently overwrite accepted DB values.

### 7.2 Atomic unit
Per-track edit is the atomic unit. Bulk edit is a batch of independent per-track operations.

### 7.3 Write path
1. Validate proposed field changes.
2. Attempt tag write for the target file.
3. If tag write succeeds, persist DB update + edit_history in one DB transaction.
4. If tag write fails, do not persist DB change; mark sync event `failed`.

### 7.4 Bulk partial failure rule
1. No global rollback across all tracks.
2. Successful tracks commit.
3. Failed tracks remain unchanged and are listed in result summary with retry action.

## 8. Conflict resolution (external change vs DB)

1. If external tag/file metadata change conflicts with DB values:
   - set `sync_status = conflict`
   - create conflict event record
   - show conflict queue in UI
2. User must choose one action per conflict:
   - **Keep DB value** (rewrite file tag from DB)
   - **Accept file value** (update DB from file)
   - **Manual merge** (field-by-field pick, then apply)
3. No automatic conflict auto-merge in v1.

## 9. Bulk edit scope

### 9.1 Editable in bulk
`title`, `artist`, `album`, `year`, `genre`, `bpm`, `musical_key`, `comment`, `track_number`

### 9.2 Never editable in bulk
`id`, `absolute_path`, `file_size_bytes`, `mtime`, `sha256`, `duration_sec`, `tag_version`, timestamps

### 9.3 UX rules
1. Preview row count and fields before apply.
2. Require confirmation for write action.
3. Show per-track success/failure output.

## 10. Duplicate detection definition

### 10.1 Exact duplicate
Match on `sha256`.

### 10.2 Candidate duplicate (fuzzy)
Scoring model:
1. normalized artist exact match: +0.4
2. normalized title exact match: +0.4
3. duration delta <= 2 seconds: +0.2

Threshold:
1. `score = 1.0`: high-confidence candidate
2. `score >= 0.8`: medium-confidence candidate

System behavior:
1. Never auto-delete or auto-merge.
2. Present candidate groups with manual actions: ignore, mark duplicate group, open compare.

## 11. Data model (v1)

### 11.1 `tracks`
- `id` uuid pk
- `absolute_path` text unique not null
- `file_name` text not null
- `extension` text not null
- `file_size_bytes` bigint not null
- `mtime` timestamptz not null
- `sha256` text null
- `duration_sec` numeric(10,3) null
- `title` text null
- `artist` text null
- `album` text null
- `year` int null
- `genre` text null
- `bpm` numeric(6,2) null
- `musical_key` text null
- `comment` text null
- `track_number` text null
- `tag_version` text null  (format-specific tag standard, e.g., `ID3v2.4`, `VorbisComment`)
- `sync_status` text not null default `pending`
- `last_tag_read_at` timestamptz null
- `last_tag_write_at` timestamptz null
- `missing_at` timestamptz null
- `created_at` timestamptz not null
- `updated_at` timestamptz not null

### 11.2 `sync_events`
- `id` uuid pk
- `track_id` uuid fk
- `event_type` text not null
- `status` text not null
- `error_message` text null
- `payload` jsonb not null default `'{}'::jsonb`
- `created_at` timestamptz not null

### 11.3 `edit_history`
- `id` uuid pk
- `track_id` uuid fk
- `field_name` text not null
- `old_value` text null
- `new_value` text null
- `edited_by` text not null default `local_user`
- `created_at` timestamptz not null

### 11.4 Retention policy
1. Keep `edit_history` for 18 months.
2. Monthly pruning job deletes older rows.

## 12. Sync status state machine

Statuses:
1. `pending`
2. `synced`
3. `error`
4. `conflict`
5. `missing`

Transitions:
1. `pending -> synced` on successful parse/write cycle.
2. `pending -> error` on ingest/write failure.
3. `synced -> conflict` on external divergent change.
4. `error -> pending` on retry start.
5. `conflict -> pending` on user resolution apply.
6. `* -> missing` when file deleted on disk.
7. `missing -> pending` if file reappears and is re-linked.

## 13. Performance and quality targets (testable)

Test profile:
1. macOS 14+, Apple M1 16 GB RAM.
2. Library size: 50,000 tracks metadata rows.

Targets:
1. Initial scan starts UI within 3 seconds and runs in background.
2. Search query on indexed fields returns first page in <= 300 ms (p95).
3. Main thread frame stalls >100 ms must not occur during steady-state browsing.
4. 95% of single-track metadata writes complete in <= 500 ms excluding disk contention.

## 14. Accessibility and UX baseline

1. Dark mode default with light mode option.
2. Minimum supported window size: 1280x800.
3. Full keyboard navigation for table selection, edit, confirm, and conflict actions.
4. High-contrast status badges for `error` and `conflict`.

## 15. Repository and delivery expectations

1. Store PRD under `docs/PRD.md`.
2. Track key decisions as ADRs.
3. Keep schema as SQL migrations plus DBML.
4. Build tests before feature implementation in highest-risk modules.

## 16. Milestones

1. **M1: Specs and scaffold**
   - ADRs, specs, migrations, seed data, package skeleton, onboarding docs.
2. **M2: Metadata and sync core**
   - scanner, watcher, reconciler, tag read/write roundtrip tests.
3. **M3: GUI workflows**
   - library table, detail editing, bulk edit, sync/conflict center.
4. **M4: hardening**
   - performance tuning, packaging prep, QA for edge-case formats.
