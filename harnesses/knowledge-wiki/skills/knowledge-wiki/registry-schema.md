<!-- Registry schema — 2026-04-08 -->

# ~/.claude/wikis.json Schema

The global wiki registry. A single JSON file that maps wiki names to absolute paths.

## Format

    {
      "version": 1,
      "wikis": [
        {
          "name": "knowledge-wiki",
          "path": "/Users/macbookair/knowledge-wiki/wiki",
          "description": "Claude Code skill framework design, subagent patterns, governance",
          "registered": "2026-04-08",
          "last_used": "2026-04-08"
        }
      ]
    }

## Top-level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | integer | yes | Schema version. Currently 1. |
| wikis | array | yes | List of registered wikis. May be empty. |

## Wiki Entry Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | yes | Unique kebab-case identifier. No spaces, lowercase. |
| path | string | yes | Canonical absolute path. Resolved via realpath, no trailing slash. |
| description | string | yes | Human-readable summary for inference matching. May be empty string. |
| registered | string | yes | ISO date (YYYY-MM-DD) of registration. |
| last_used | string | yes | ISO date of last successful write operation. Read-only ops do not update this. |
| staleness_rules | object | no | Domain-configurable staleness thresholds. See below. |
| consolidation | object | no | Consolidation pipeline configuration. See below. |

## Staleness Rules (Optional)

When present in a wiki entry, `staleness_rules` configures per-wiki staleness thresholds for wiki-health check 13 (see `lifecycle-spec.md` for the state machine):

```json
{
  "staleness_rules": {
    "default_days": 180,
    "overrides": [
      { "tags": ["sanctions", "pep-lists"], "days": 30 },
      { "tags": ["regulations", "directives"], "days": 90 },
      { "tags": ["typologies", "methodologies"], "days": 365 }
    ]
  }
}
```

- `default_days` (integer, required if block present): fallback threshold for articles with no tag-specific override.
- `overrides` (array, optional): tag-specific thresholds. Tag-specific overrides take precedence over `default_days`. If an article matches multiple overrides, the shortest (most aggressive) threshold wins.

These thresholds are also stored in the wiki's own `schema.md` (authoritative). The registry copy is for quick access by skills that need thresholds without reading schema.md.

## Consolidation Config (Optional)

When present, `consolidation` configures the dedup pipeline for `wiki-consolidate`:

```json
{
  "consolidation": {
    "dedup_cosine_threshold": 0.85
  }
}
```

- `dedup_cosine_threshold` (float, default 0.85): cosine similarity threshold for flagging potential duplicates during consolidation. Domain-dependent — AML regulatory text may need 0.80 (formulaic language inflates similarity), ML research may use 0.90 (more semantically diverse).

## Invariants

- `name` is unique across all entries.
- `path` should be unique, but is not strictly enforced (two names pointing to the same path is allowed but discouraged).
- `domain` is NOT cached here — it is read from the wiki's own `schema.md` on demand to prevent drift.

## Lifecycle

- Created lazily: the file does not exist until the first wiki is registered.
- All mutations use the atomic rename pattern: write `.tmp`, then `mv` to final path.
- Read-only skills (wiki-query, wiki-health in read modes) do not mutate the registry.
- Corrupted files are never auto-repaired — users must back up and delete manually.

## Canonical Path

"Canonical path" in this document means the absolute path with symlinks resolved (via `realpath`) and trailing slashes stripped. Use the Bash tool to run `realpath <path>` when comparing paths or storing them in the registry.
