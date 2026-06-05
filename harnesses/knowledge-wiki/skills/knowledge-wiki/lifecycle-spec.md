<!-- Canonical lifecycle state machine — SSOT for all wiki skills -->
<!-- REFERENCE, DO NOT PASTE. Skills that handle lifecycle logic should link here rather than duplicate definitions. -->

# Article Lifecycle

Five-state lifecycle for wiki articles. Every article has exactly one `status` value.

## State Machine

```
draft → reviewed → verified → stale → archived
             ↓                   ↓
             └───────────────────┘ (reviewed can also go stale)
  ↑        ↑                     ↓
  └────────┴─────────────────────┘ (re-verify: back to draft)
```

## State Definitions

| Status | Meaning | Transitions From | Transitions To |
|--------|---------|------------------|----------------|
| `draft` | Newly created, not yet reviewed | (initial), stale | reviewed |
| `reviewed` | Passed reviewer subagent checks | draft | verified |
| `verified` | Human-confirmed or high-confidence | reviewed | stale |
| `stale` | Exceeded domain staleness threshold | verified, reviewed | draft (re-verify), archived |
| `archived` | Explicitly retired, excluded from query | stale | (terminal) |

## Default Status by Skill

| Skill | Initial Status | Rationale |
|-------|---------------|-----------|
| wiki-absorb | `reviewed` | Articles pass reviewer subagent during absorb |
| wiki-bootstrap | `draft` | Bootstrap articles need human review |
| wiki-add (capture) | `draft` | Quick captures need review before promotion |
| wiki-add (ingest) | `draft` | Ingested content needs review |
| synthesize (contrib) | `draft` | Synthesized content needs validation |
| wiki-consolidate | `draft` | Consolidated facts need review |
| wiki-reorg | Preserves existing status | Reorg restructures, doesn't change lifecycle |

## Staleness Thresholds

Staleness is domain-configurable via `staleness_rules` in the wiki's `schema.md`:

```yaml
staleness_rules:
  default_days: 180
  overrides:
    - tags: [sanctions, pep-lists]
      days: 30
    - tags: [regulations, directives]
      days: 90
    - tags: [typologies, methodologies]
      days: 365
```

Tag-specific overrides take precedence over `default_days`. When an article matches multiple tag overrides (e.g., an article tagged both `sanctions` and `regulations`), the shortest (most aggressive) threshold wins. An article is stale when `days_since_update > applicable_threshold` and its current status is `verified` or `reviewed`.

## Frontmatter

```yaml
status: draft | reviewed | verified | stale | archived
```

## Validation

- wiki-health check 12 (Status Validity): every article must have `status` field with a valid lifecycle value. Severity: ERROR.
- wiki-health check 13 (Staleness Detection): articles with `status: verified` or `reviewed` past their staleness threshold. Severity: WARNING.
