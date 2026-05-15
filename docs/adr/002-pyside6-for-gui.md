# ADR 002: Use PySide6 for desktop GUI

## Status
Accepted

## Context
The app requires a native-feeling macOS desktop UI with large-table interactions, dialogs, and keyboard-friendly workflows.

## Decision
Use PySide6 for the v1 GUI layer.

## Consequences
1. GUI modules live under `cratepilot/gui/`.
2. UI patterns favor table + detail + modal flows.
3. macOS-only UX assumptions are acceptable in v1.
