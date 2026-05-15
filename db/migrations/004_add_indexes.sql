CREATE INDEX IF NOT EXISTS idx_tracks_artist ON tracks (artist);
CREATE INDEX IF NOT EXISTS idx_tracks_title ON tracks (title);
CREATE INDEX IF NOT EXISTS idx_tracks_year ON tracks (year);
CREATE INDEX IF NOT EXISTS idx_tracks_genre ON tracks (genre);
CREATE INDEX IF NOT EXISTS idx_tracks_bpm ON tracks (bpm);
CREATE INDEX IF NOT EXISTS idx_tracks_musical_key ON tracks (musical_key);
CREATE INDEX IF NOT EXISTS idx_tracks_sync_status ON tracks (sync_status);
CREATE INDEX IF NOT EXISTS idx_sync_events_track_id ON sync_events (track_id);
CREATE INDEX IF NOT EXISTS idx_sync_events_created_at ON sync_events (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_edit_history_track_id ON edit_history (track_id);
CREATE INDEX IF NOT EXISTS idx_edit_history_created_at ON edit_history (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_tracks_search_tsv
ON tracks
USING GIN (
  to_tsvector(
    'simple',
    coalesce(title, '') || ' ' ||
    coalesce(artist, '') || ' ' ||
    coalesce(comment, '')
  )
);
