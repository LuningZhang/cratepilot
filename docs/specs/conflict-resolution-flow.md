# Conflict Resolution Flow (v1)

## Conflict condition
A filesystem-triggered metadata read differs from current DB values for one or more managed fields.

## User-visible flow
1. Track is marked `conflict`.
2. Track appears in Conflict Queue view.
3. User opens field-by-field diff.
4. User selects one action:
   - Keep DB value
   - Accept file value
   - Manual merge
5. System executes per-track write path and updates status.

## Action semantics
1. **Keep DB value**: write DB fields to file, keep DB unchanged.
2. **Accept file value**: apply file values to DB and `edit_history`.
3. **Manual merge**: user-selected field blend writes to file then DB.

## Guardrails
1. No silent overwrite in background.
2. Conflicts must be user-resolved.
3. Failed resolution attempts move to `error` with retry.
