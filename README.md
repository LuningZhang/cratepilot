# CratePilot

macOS-first local DJ library manager scaffold.

## Current status
This repository currently contains:
1. Refined product requirements in `docs/PRD.md`
2. ADR and spec documents in `docs/`
3. DB migrations and seed data in `db/`
4. Python package scaffold in `cratepilot/`
5. Test skeletons in `tests/`

## Next implementation order
1. Build metadata adapter and roundtrip tests.
2. Implement scanner + watcher + reconciliation.
3. Add GUI flows for library, detail, bulk edit, and conflict queue.
