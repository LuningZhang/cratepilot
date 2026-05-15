# Sync State Machine (v1)

## States
1. `pending`
2. `synced`
3. `error`
4. `conflict`
5. `missing`

## Triggers and transitions
| From | Trigger | To | Notes |
|---|---|---|---|
| pending | parse/write success | synced | Normal ingest/edit completion |
| pending | parse/write failure | error | Store failure details in `sync_events` |
| synced | external divergent file change | conflict | Requires user decision |
| error | retry queued | pending | Retry starts new attempt |
| conflict | user selects resolution action | pending | Resolution reapplies write path |
| any | file deleted from disk | missing | Soft-missing state |
| missing | file returns/relinked | pending | Re-ingest candidate |

## Rules
1. `conflict` never auto-resolves.
2. `error` may auto-retry only for transient IO/lock errors.
3. Every transition writes one `sync_events` row.
