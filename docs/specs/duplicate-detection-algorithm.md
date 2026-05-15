# Duplicate Detection Algorithm (v1)

## Two-tier model

### Tier A: Exact duplicates
1. Compute SHA-256 hash (background queue allowed).
2. Group tracks by identical hash.
3. Show as exact-duplicate groups.

### Tier B: Candidate duplicates
Score pairwise candidates:
1. normalized artist exact match: +0.4
2. normalized title exact match: +0.4
3. duration difference <= 2s: +0.2

Threshold classes:
1. score 1.0 -> high confidence
2. score >= 0.8 -> medium confidence

## User actions
1. Mark as reviewed.
2. Add to duplicate group.
3. Ignore candidate pair.

## Constraints
1. No auto-delete.
2. No auto-merge.
3. All actions are reversible via edit history / event log.
