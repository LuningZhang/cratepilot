CREATE TABLE IF NOT EXISTS edit_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id UUID NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    edited_by TEXT NOT NULL DEFAULT 'local_user',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
