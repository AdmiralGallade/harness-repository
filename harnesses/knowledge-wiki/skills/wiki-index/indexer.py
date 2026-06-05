#!/usr/bin/env python3
"""Build a wiki search index with FTS5 full-text search and xxHash change detection."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import time
from dataclasses import dataclass

import xxhash

from wikilib import EMBED_MODEL, EMBED_DIM, _HAS_VECTORS, _serialize_f32, parse_frontmatter

if _HAS_VECTORS:
    from fastembed import TextEmbedding
    import sqlite_vec


# --- Article parsing layer ---


@dataclass
class Article:
    slug: str
    path: str
    title: str
    content: str
    content_hash: str
    tier: str | None
    updated_at: str


def parse_article(fpath: str, wiki_path: str) -> Article:
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    slug = os.path.splitext(os.path.basename(fpath))[0]
    rel_path = os.path.relpath(fpath, wiki_path)
    content_hash = xxhash.xxh64_hexdigest(content)
    meta = parse_frontmatter(content)
    title = meta.get("title", slug.replace("-", " ").title())
    tier = meta.get("tier")
    updated_at = meta.get("timestamp", meta.get("updated", meta.get("created", "")))
    return Article(
        slug=slug,
        path=rel_path,
        title=title,
        content=content,
        content_hash=content_hash,
        tier=tier,
        updated_at=updated_at,
    )


def crawl_wiki(wiki_path: str) -> list[str]:
    paths = []
    for subdir in ("articles", "episodic"):
        root = os.path.join(wiki_path, subdir)
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    paths.append(os.path.join(dirpath, fn))
    return paths


# --- Database layer ---

SCHEMA_SQL = """\
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    tier TEXT,
    updated_at TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
    title, content, content='articles', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
END;

CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
    INSERT INTO articles_fts(articles_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
    INSERT INTO articles_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;
"""


VECTOR_SCHEMA_SQL = f"""\
CREATE VIRTUAL TABLE IF NOT EXISTS articles_vec USING vec0(
    id INTEGER PRIMARY KEY,
    embedding float[{EMBED_DIM}]
);
"""


def init_db(db_path: str, rebuild: bool = False, use_vectors: bool = False) -> sqlite3.Connection:
    if rebuild and os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    if use_vectors:
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        conn.executescript(VECTOR_SCHEMA_SQL)
    return conn


def get_existing_hashes(conn: sqlite3.Connection) -> dict[str, str]:
    return dict(conn.execute("SELECT slug, content_hash FROM articles").fetchall())


def upsert_article(conn: sqlite3.Connection, a: Article, exists: bool) -> None:
    if exists:
        conn.execute(
            "UPDATE articles SET path=?, title=?, content=?, content_hash=?, tier=?, updated_at=? WHERE slug=?",
            (a.path, a.title, a.content, a.content_hash, a.tier, a.updated_at, a.slug),
        )
    else:
        conn.execute(
            "INSERT INTO articles (slug, path, title, content, content_hash, tier, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (a.slug, a.path, a.title, a.content, a.content_hash, a.tier, a.updated_at),
        )


def delete_stale(conn: sqlite3.Connection, stale_slugs: set[str]) -> None:
    for slug in stale_slugs:
        conn.execute("DELETE FROM articles WHERE slug=?", (slug,))


def update_meta(conn: sqlite3.Connection, has_vectors: bool = False) -> int:
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    for k, v in [
        ("version", "1"),
        ("built_at", time.strftime("%Y-%m-%dT%H:%M:%S")),
        ("has_vectors", str(has_vectors).lower()),
        ("article_count", str(count)),
    ]:
        conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (k, v))
    return count


# --- Embedding layer ---


def embed_articles(conn: sqlite3.Connection) -> int:
    rows = conn.execute(
        "SELECT a.id, a.title, a.content FROM articles a"
        " WHERE a.id NOT IN (SELECT id FROM articles_vec)"
    ).fetchall()
    if not rows:
        return 0
    model = TextEmbedding(model_name=EMBED_MODEL)
    texts = [f"{r[1]}\n{r[2]}" for r in rows]
    embeddings = list(model.embed(texts))
    for row, emb in zip(rows, embeddings):
        truncated = list(emb[:EMBED_DIM])
        conn.execute(
            "INSERT INTO articles_vec (id, embedding) VALUES (?, ?)",
            (row[0], _serialize_f32(truncated)),
        )
    return len(rows)


# --- Build orchestration ---


def build_index(wiki_path: str, rebuild: bool = False, no_vectors: bool = False) -> int:
    start = time.monotonic()
    db_path = os.path.join(wiki_path, ".wiki-index.db")
    use_vectors = _HAS_VECTORS and not no_vectors

    conn = init_db(db_path, rebuild=rebuild, use_vectors=use_vectors)
    existing = get_existing_hashes(conn)

    file_paths = crawl_wiki(wiki_path)
    seen: set[str] = set()
    updated_slugs: set[str] = set()
    new_count = 0
    updated_count = 0
    skipped_count = 0

    for fpath in file_paths:
        article = parse_article(fpath, wiki_path)
        seen.add(article.slug)

        if article.slug in existing:
            if existing[article.slug] == article.content_hash:
                skipped_count += 1
                continue
            upsert_article(conn, article, exists=True)
            updated_slugs.add(article.slug)
            updated_count += 1
        else:
            upsert_article(conn, article, exists=False)
            new_count += 1

    stale = set(existing) - seen

    vec_count = 0
    if use_vectors:
        for slug in updated_slugs | stale:
            conn.execute(
                "DELETE FROM articles_vec WHERE id = (SELECT id FROM articles WHERE slug = ?)",
                (slug,),
            )
        delete_stale(conn, stale)
        vec_count = embed_articles(conn)
        total_vecs = conn.execute("SELECT COUNT(*) FROM articles_vec").fetchone()[0]
        has_vecs = total_vecs > 0
    else:
        delete_stale(conn, stale)
        row = conn.execute("SELECT value FROM meta WHERE key = 'has_vectors'").fetchone()
        has_vecs = row is not None and row[0] == "true"

    total = update_meta(conn, has_vectors=has_vecs)
    conn.commit()
    conn.close()

    elapsed = time.monotonic() - start
    print(f"Indexed: {total} articles ({new_count} new, {updated_count} updated, {skipped_count} skipped)")
    if use_vectors:
        print(f"Vectors: {vec_count} embedded")
    else:
        print("Vectors: skipped (no fastembed)")
    print(f"Time: {elapsed:.1f}s")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build wiki search index")
    sub = parser.add_subparsers(dest="command")
    bp = sub.add_parser("build", help="Build or update the search index")
    bp.add_argument("--wiki-path", required=True, help="Path to wiki root")
    bp.add_argument("--rebuild", action="store_true", help="Drop and recreate the index")
    bp.add_argument("--no-vectors", action="store_true", help="Skip vector embeddings")

    args = parser.parse_args()
    if args.command != "build":
        parser.print_help()
        return 1

    wiki_path = os.path.abspath(args.wiki_path)
    if not os.path.isdir(os.path.join(wiki_path, "articles")):
        print(f"Error: No articles directory at {wiki_path}", file=sys.stderr)
        return 1

    return build_index(wiki_path, rebuild=args.rebuild, no_vectors=args.no_vectors)


if __name__ == "__main__":
    sys.exit(main())
