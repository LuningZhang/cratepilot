# ADR 003: PostgreSQL as source of truth

## Status
Accepted

## Context
The app must support robust querying, indexing, history, and deterministic metadata workflows at local-library scale.

## Decision
Use local PostgreSQL as authoritative source for accepted app edits. External file changes produce explicit conflicts; they do not auto-overwrite DB data.

## Consequences
1. Conflict queue is mandatory.
2. Tag writes and DB commits follow defined per-track atomic unit rules.
3. Schema and migrations are first-class artifacts.
