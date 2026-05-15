CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    absolute_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    extension TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mtime TIMESTAMPTZ NOT NULL,
    sha256 TEXT,
    duration_sec NUMERIC(10,3),
    title TEXT,
    artist TEXT,
    album TEXT,
    year INT,
    genre TEXT,
    bpm NUMERIC(6,2),
    musical_key TEXT,
    comment TEXT,
    track_number TEXT,
    tag_version TEXT,
    sync_status TEXT NOT NULL DEFAULT 'pending',
    last_tag_read_at TIMESTAMPTZ,
    last_tag_write_at TIMESTAMPTZ,
    missing_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
