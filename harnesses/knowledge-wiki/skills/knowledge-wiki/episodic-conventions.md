<!-- Canonical episodic entry format — SSOT -->
<!-- REFERENCE, DO NOT PASTE. Skills that read/write episodic entries should link here. -->

# Episodic Entry Conventions

Episodic entries are append-only records of what happened — session logs, task traces, research findings, worker outputs. They live in `<wiki_path>/episodic/` and are distinct from articles.

## Key Properties

- Content body is **NEVER modified** after creation (immutable below frontmatter fence)
- Are **NEVER absorbed** directly — they feed the consolidation pipeline (wiki-consolidate)
- Are **NOT indexed** in `index.md` (discovered via filesystem listing or search index)
- **ARE searchable** via the search index (Phase 2)
- Carry `worker` and `task_id` fields for provenance tracking

## Directory

```
<wiki_path>/
  episodic/           # Append-only session/worker logs
```

## Filename Pattern

```
YYYY-MM-DDTHH-MM-SS-<slug>.md
```

Use ISO timestamp with hyphens replacing colons (filesystem-safe). Slug follows standard slugification rules.

## Frontmatter Format

```yaml
---
timestamp: 2026-04-25T14:30:00Z
worker: claude-code | qwen-local | nanaclaw
task_id: research-tbml-typologies-001
tags: [tbml, trade-based-laundering]
wiki: aml-compliance
---
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| timestamp | ISO 8601 datetime | When the entry was created |
| worker | string | Who created it: `claude-code`, `qwen-local`, `nanaclaw`, or other caller identifier |
| task_id | string | Identifier for the task/research that produced this entry |
| tags | string[] | Topic tags for search and consolidation grouping |
| wiki | string | Name of the target wiki (matches registry name) |

## Body Format

```markdown
## Research: <Topic>

[raw findings, observations, extracted facts, source URLs]

## Sources Consulted
- [url or file path]
- [url or file path]
```

The body structure is flexible — the key requirement is that findings and sources are present. The `## Sources Consulted` section is strongly recommended for public-tier consolidation.

## Consolidation Metadata (The One Permitted Mutation)

After `/wiki-consolidate` processes an episodic entry, these fields are **appended to the frontmatter**:

```yaml
consolidated_at: 2026-04-25T15:00:00Z
consolidation_result: extracted | duplicate | low-confidence
facts_extracted: 3
inbox_entries: [2026-04-25-tbml-red-flags.md, 2026-04-25-tbml-case-study.md]
```

| Field | Type | Description |
|-------|------|-------------|
| consolidated_at | ISO 8601 datetime | When consolidation processed this entry |
| consolidation_result | enum | `extracted` (facts pulled), `duplicate` (already covered), `low-confidence` (flagged) |
| facts_extracted | integer | Number of candidate facts identified |
| inbox_entries | string[] | Filenames of inbox entries produced from this episodic entry |

**Rule:** Only these frontmatter fields may be added. The content body (everything below the `---` frontmatter fence) is immutable. This preserves raw research findings while allowing lifecycle tracking.

## Consolidation Tracking

A `.consolidated` marker file in `episodic/` provides fast-scan indexing (avoids re-reading every entry to check `consolidated_at`). The episodic entry's own frontmatter is the source of truth for its consolidation state.

## Relationship to Articles

Episodic entries are NOT articles:
- They do not have `tier` or `status` frontmatter (they are implicitly tier: episodic)
- They are exempt from all article-level lint checks (checks 1-13; check 13 staleness doesn't apply — no status field)
- They are not listed in `index.md`
- They cannot be parents or children in the article hierarchy
