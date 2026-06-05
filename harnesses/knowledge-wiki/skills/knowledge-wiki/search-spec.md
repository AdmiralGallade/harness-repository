# Search Specification

Hybrid BM25 + vector search for wiki articles. SSOT for the search system — referenced by wiki-query SKILL.md and wiki-index SKILL.md.

## Dependencies

| Package | Minimum Version | Role |
|---------|----------------|------|
| fastembed | >=0.4 | ONNX embedding runtime (nomic-embed-text) |
| sqlite-vec | >=0.1.9 | SQLite vector extension |
| xxhash | >=3.0 | Fast content hashing for change detection |

All deps listed in `skills/wiki-index/requirements.txt`. Invoked via `uv run --with-requirements skills/wiki-index/requirements.txt python skills/wiki-index/<script>`.

## Index Schema

Per-wiki SQLite database at `<wiki_path>/.wiki-index.db`. WAL journal mode.

```sql
-- Metadata
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
-- key: 'version', 'built_at', 'has_vectors', 'article_count'

-- Articles with content hashes
CREATE TABLE articles (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,  -- xxHash hex digest
    tier TEXT,                    -- public/private/episodic
    updated_at TEXT
);

-- Full-text search (BM25)
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, content, content='articles', content_rowid='id'
);

-- Vector embeddings (cosine similarity)
-- Only created when fastembed is available
CREATE VIRTUAL TABLE articles_vec USING vec0(
    id INTEGER PRIMARY KEY,
    embedding float[384]         -- nomic-embed-text dimension
);
```

## CLI Interface

### indexer.py

```
usage: indexer.py build --wiki-path <path> [--rebuild] [--no-vectors]

Commands:
  build         Build or update the search index

Options:
  --wiki-path   Absolute path to wiki root (required)
  --rebuild     Drop and recreate the entire index (idempotent)
  --no-vectors  Skip vector embedding (FTS5 only)

Output (stdout):
  Indexed: N articles (M new, K updated, J skipped)
  Vectors: N embedded | skipped (no fastembed)
  Time: Xs

Exit codes:
  0  Success
  1  Error (wiki-path missing, DB write failure)
```

Crawls `<wiki_path>/articles/` and `<wiki_path>/episodic/` recursively for `.md` files. Parses YAML frontmatter for title and tier. Content = full file text (per-article chunking).

### search.py

```
usage: search.py <command> --wiki-path <path> [options]

Commands:
  query         Run a search query
  precision     Validate precision against ground-truth queries

Query options:
  --wiki-path   Absolute path to wiki root (required)
  --query       Search query string (required for query command)
  --top N       Return top N results (default: 10)
  --bm25-only   Skip vector search, use BM25 only
  --alpha F     Semantic weight for RRF (default: 0.4)
  --rrf-k N     RRF constant (default: 60)

Query output (stdout, one line per result):
  <rank>. <slug> (score: <float>) -- <title>

Precision options:
  --queries     Path to ground-truth queries YAML (required)

Precision output (stdout):
  Query: "<query>" — P@3: <float> — hits: <slug1>, <slug2>, ...
  ...
  Mean P@3: <float> (threshold: 0.8)

Exit codes:
  0  Success (precision >= threshold for precision command)
  1  Error or precision below threshold
```

## Scoring Algorithm

### Hybrid Search (default)

1. **BM25 query** via FTS5: `SELECT slug, rank FROM articles_fts WHERE articles_fts MATCH ?`
2. **Vector query** via sqlite-vec: compute query embedding with fastembed, `SELECT slug, distance FROM articles_vec WHERE embedding MATCH ? ORDER BY distance LIMIT ?`
3. **RRF fusion**: For each article appearing in either list (using positional rank 1, 2, 3...):
   ```
   rrf_score = alpha * (1 / (rrf_k + vector_rank)) + (1 - alpha) * (1 / (rrf_k + bm25_rank))
   ```
   Where `alpha` = semantic weight (default 0.4), `rrf_k` = 60.
5. **Sort** by rrf_score descending, return top N.

### BM25-Only Fallback

When fastembed is unavailable or `--bm25-only` is passed:
- Skip step 2 (vector query)
- Return FTS5 results ranked by BM25 score directly

## Fallback Chain

Wiki-query Step 1 uses this fallback chain (first available wins):

| Tier | Condition | Search Method |
|------|-----------|---------------|
| 1 | `.wiki-index.db` exists + fastembed available | Full hybrid (BM25 + vector + RRF) |
| 2 | `.wiki-index.db` exists, no fastembed | BM25-only via search.py --bm25-only |
| 3 | No `.wiki-index.db` | Keyword scoring (inlined in wiki-query/SKILL.md Step 1) |

## Ground-Truth Test Format

File: `tests/fixtures/search/queries.yaml`

```yaml
queries:
  - query: "How does X work?"
    expected_top3:
      - article-slug-a
      - article-slug-b
      - article-slug-c
  - query: "What is the difference between Y and Z?"
    expected_top3:
      - article-slug-d
      - article-slug-e
      - article-slug-f

threshold: 0.8  # minimum mean precision@3
```

Precision@3 = (number of expected slugs in actual top-3) / 3, averaged across all queries.

## Performance Target

Index build: <10s for 100 articles on M1 Max (warm fastembed model cache).

## Change Detection

xxHash of full file content (frontmatter + body). On incremental build:
- Hash each `.md` file in articles/ and episodic/
- Compare against stored `content_hash` in articles table
- Re-index only files with changed or missing hashes
- Remove DB rows for deleted files
