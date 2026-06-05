# Dashboard Metrics Specification

Companion to wiki-health SKILL.md. Defines the 12 computed metrics and the dashboard output format.

## Dashboard Format

```
Wiki Health -- {{domain from schema.md}}
======================================

Articles: N total
  concepts:     X
  patterns:     X
  decisions:    X
  action-plans: X

Inbox: N entries pending (/wiki-absorb to process)

Links:
  Cross-links:    N
  Avg per article: N.N
  Orphaned:       N

Tags: N unique
  Top 5: tag-a (N), tag-b (N), tag-c (N), tag-d (N), tag-e (N)

Hierarchy:
  Hub articles: N (articles with 3+ children)
  Max depth:    N
  Roots:        N (list root names)

Tiers:
  public:       X
  private:      X

Lifecycle:
  draft:        X
  reviewed:     X
  verified:     X
  stale:        X
  archived:     X

Episodic: N entries (N unconsolidated)

Schema Health:
  Dead tags:    N
  Missing tags: N
  Drift score:  LOW | MEDIUM | HIGH

Recent Activity (from log.md):
  [date] OPERATION -- summary
  ...last 5 entries
```

## Computed Metrics

| # | Metric | How to Compute |
|---|--------|----------------|
| 1 | Article count by category | Count `.md` (excl `.gitkeep`) per `<wiki_path>/articles/` subdirectory |
| 2 | Inbox count | Count `.md` in `<wiki_path>/inbox/`, excl `.gitkeep` and `.processed/` |
| 3 | Cross-link count | Count all `[[link]]` occurrences in article bodies |
| 4 | Avg links per article | Total cross-links / total articles (1 decimal) |
| 5 | Orphan count | Articles with zero inbound `[[links]]` from other articles |
| 6 | Tag frequency + top 5 | Count articles per tag from frontmatter; top 5 by frequency |
| 7 | Hub count | Articles listed as parent by 3+ other articles |
| 8 | Max depth | Longest root→child chain; root depth = 1 |
| 9 | Root articles | Articles with `parents: []`; count and list filenames |
| 10 | Schema health | Dead tags (in schema, 0 uses) + missing tags (3+ uses, not in schema). Drift: LOW 0-1, MEDIUM 2-4, HIGH 5+ |
| 11 | Tier breakdown | Count per `tier` value (`public`/`private`). See `tier-spec.md` |
| 12 | Lifecycle breakdown | Count per `status` value. See `lifecycle-spec.md` |
| 13 | Episodic count | Count `.md` in `<wiki_path>/episodic/`; unconsolidated = lacking `consolidated_at` |

## Edge Cases

- **Empty wiki**: Show minimal dashboard, all counts zero, suggest `/wiki-add`.
- **No cross-links**: Show 0, all articles orphaned. Suggest `/wiki-reorg`.
- **No tags**: Show 0 unique, omit Top 5.
- **No hierarchy**: Hub=0, depth=1, all articles are roots.
- **schema.md missing**: Use "Unknown Domain", skip Schema Health.
- **log.md missing**: "No activity recorded yet."
