---
name: wiki-index
description: "Build and manage the hybrid search index for a wiki. Creates a per-wiki SQLite database with FTS5 full-text search and optional vector embeddings. Use when wiki has 50+ articles or search quality needs improving. Do NOT use for querying — use wiki-query (which calls search automatically)."
reads: [<wiki_path>/articles/**/*.md, <wiki_path>/episodic/**/*.md, <wiki_path>/.wiki-index.db]
writes: [<wiki_path>/.wiki-index.db]
dispatches: []
tier: single-agent
---

# wiki-index

Build a hybrid search index over wiki articles and episodic entries. Produces a per-wiki SQLite database (`.wiki-index.db`) with FTS5 full-text search and optional sqlite-vec vector embeddings.

## Pre-checks

1. **Python available:** Verify `python3 --version` returns 3.11+. If not: "Python 3.11+ required for wiki-index." STOP.
2. **uv available:** Verify `uv --version` returns 0.7+. If not: "uv 0.7+ required. Install: https://docs.astral.sh/uv/" STOP.
3. **Wiki path valid:** Verify `<wiki_path>/articles/` exists. If not: "No articles directory at <wiki_path>. Is this a valid wiki?" STOP.

## Invocation

All commands use `uv run --with-requirements` for portable dependency management:

```bash
# Build or incrementally update the index
uv run --with-requirements ~/.claude/skills/wiki-index/requirements.txt \
  python ~/.claude/skills/wiki-index/indexer.py build --wiki-path <wiki_path>

# Full rebuild (drop and recreate)
uv run --with-requirements ~/.claude/skills/wiki-index/requirements.txt \
  python ~/.claude/skills/wiki-index/indexer.py build --wiki-path <wiki_path> --rebuild

# Build without vector embeddings (FTS5 only)
uv run --with-requirements ~/.claude/skills/wiki-index/requirements.txt \
  python ~/.claude/skills/wiki-index/indexer.py build --wiki-path <wiki_path> --no-vectors

# Search (used by wiki-query, not typically invoked directly)
uv run --with-requirements ~/.claude/skills/wiki-index/requirements.txt \
  python ~/.claude/skills/wiki-index/search.py query --wiki-path <wiki_path> --query "<query>" --top 10
```

When skills are installed to `~/.claude/skills/`, the paths above work directly. When running from the project repo, use `skills/wiki-index/` relative paths instead.

## When to Build

- **First time:** After wiki reaches ~50 articles, suggest building an index.
- **After wiki-absorb:** If the index exists and articles were added/modified, rebuild incrementally.
- **After wiki-reorg:** If articles were moved/renamed, do a full `--rebuild`.
- **Manual:** User invokes `/wiki-index` directly.

## Graceful Degradation

The indexer handles missing optional dependencies:
- **Without fastembed:** Builds FTS5-only index (BM25 search works, no vector similarity)
- **Without sqlite-vec:** Builds FTS5-only index (same as above)
- **Both available:** Full hybrid index (BM25 + vector)

See `~/.claude/skills/knowledge-wiki/search-spec.md` for the complete specification.

## Output

The index is stored at `<wiki_path>/.wiki-index.db`. This file:
- MUST be in `.gitignore` (it's a derived artifact)
- Is rebuilt from source `.md` files at any time
- Uses WAL journal mode for safe concurrent reads
