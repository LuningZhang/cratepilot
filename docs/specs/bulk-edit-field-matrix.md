# Bulk Edit Field Matrix (v1)

| Field | Bulk editable | Reason |
|---|---|---|
| title | Yes | Curated metadata |
| artist | Yes | Curated metadata |
| album | Yes | Curated metadata |
| year | Yes | Curated metadata |
| genre | Yes | Curated metadata |
| bpm | Yes | Curated metadata |
| musical_key | Yes | Curated metadata |
| comment | Yes | Curated metadata |
| track_number | Yes | Curated metadata |
| absolute_path | No | File identity field |
| sha256 | No | Integrity field |
| file_size_bytes | No | Derived from file |
| mtime | No | Derived from filesystem |
| duration_sec | No | Parsed measurement |
| tag_version | No | Parser-derived |
| created_at / updated_at | No | System-managed |

## UX behavior
1. Show selected row count and affected fields before apply.
2. Confirm action before write.
3. Return per-track success/failure report.
