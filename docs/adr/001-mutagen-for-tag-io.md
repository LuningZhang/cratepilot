# ADR 001: Use Mutagen for tag I/O

## Status
Accepted

## Context
CratePilot needs read/write metadata support across MP3, FLAC, WAV, AIFF, and M4A/AAC with consistent Python APIs.

## Decision
Use Mutagen as the single tag I/O library in v1.

## Consequences
1. Unified adapter interface in `cratepilot/metadata/adapter.py`.
2. Format-specific edge cases isolated in `cratepilot/metadata/formats/`.
3. Roundtrip tests required per format before feature code.
