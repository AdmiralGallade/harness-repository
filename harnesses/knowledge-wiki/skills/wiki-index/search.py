#!/usr/bin/env python3
"""Query a wiki's hybrid search index with BM25 + vector RRF fusion."""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys

from wikilib import EMBED_MODEL, EMBED_DIM, _HAS_VECTORS, _serialize_f32

if _HAS_VECTORS:
    from fastembed import TextEmbedding
    import sqlite_vec


def _sanitize_fts(query: str) -> str:
    tokens = re.findall(r"[a-zA-Z0-9]+", query)
    meaningful = [t for t in tokens if len(t) > 1]
    return " OR ".join(meaningful) if meaningful else query


def _open_index(wiki_path: str, bm25_only: bool = False):
    db_path = os.path.join(wiki_path, ".wiki-index.db")
    if not os.path.exists(db_path):
        print(f"Error: No index at {db_path}. Run indexer.py build.", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    use_vectors = False
    if _HAS_VECTORS and not bm25_only:
        row = conn.execute("SELECT value FROM meta WHERE key = 'has_vectors'").fetchone()
        if row and row[0] == "true":
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            use_vectors = True
    return conn, use_vectors


def _query_bm25(conn: sqlite3.Connection, query: str, limit: int) -> list[tuple[str, str]]:
    fts = _sanitize_fts(query)
    return conn.execute(
        "SELECT a.slug, a.title FROM articles_fts f"
        " JOIN articles a ON a.id = f.rowid"
        " WHERE articles_fts MATCH ? ORDER BY f.rank LIMIT ?",
        (fts, limit),
    ).fetchall()


def _query_vector(
    conn: sqlite3.Connection, query_bytes: bytes, limit: int
) -> list[tuple[str, str]]:
    rows = conn.execute(
        "SELECT id, distance FROM articles_vec"
        " WHERE embedding MATCH ? AND k = ?",
        (query_bytes, limit),
    ).fetchall()
    if not rows:
        return []
    ids = [r[0] for r in rows]
    ph = ",".join("?" * len(ids))
    info = {
        r[0]: (r[1], r[2])
        for r in conn.execute(
            f"SELECT id, slug, title FROM articles WHERE id IN ({ph})", ids
        ).fetchall()
    }
    return [(info[r[0]][0], info[r[0]][1]) for r in rows if r[0] in info]


def _rrf_fuse(bm25, vec, alpha, k, top_n):
    bm25_rank = {s: i + 1 for i, (s, _) in enumerate(bm25)}
    vec_rank = {s: i + 1 for i, (s, _) in enumerate(vec)}
    titles = dict(bm25 + vec)
    default_bm25 = len(bm25) + 1
    default_vec = len(vec) + 1
    scored = []
    for slug in set(bm25_rank) | set(vec_rank):
        br = bm25_rank.get(slug, default_bm25)
        vr = vec_rank.get(slug, default_vec)
        score = alpha * (1 / (k + vr)) + (1 - alpha) * (1 / (k + br))
        scored.append((slug, titles[slug], score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_n]


def do_search(conn, query, top_n, use_vectors, alpha, rrf_k, embed_model=None):
    fetch = max(top_n * 3, 50)
    bm25 = _query_bm25(conn, query, fetch)
    if use_vectors and embed_model is not None:
        emb = list(embed_model.embed([query]))[0][:EMBED_DIM]
        vec = _query_vector(conn, _serialize_f32(list(emb)), fetch)
        return _rrf_fuse(bm25, vec, alpha, rrf_k, top_n)
    return [
        (slug, title, (1 - alpha) / (rrf_k + i + 1))
        for i, (slug, title) in enumerate(bm25[:top_n])
    ]


def _parse_queries_yaml(path: str):
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    threshold = 0.8
    queries: list[tuple[str, list[str]]] = []
    cur_query = None
    cur_expected: list[str] = []
    reading_expected = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("threshold:"):
            threshold = float(stripped.split(":", 1)[1].strip())
            reading_expected = False
            continue
        m = re.match(r'-\s+query:\s*"([^"]+)"', stripped)
        if m:
            if cur_query is not None:
                queries.append((cur_query, cur_expected))
            cur_query = m.group(1)
            cur_expected = []
            reading_expected = False
            continue
        if stripped == "expected_top3:":
            reading_expected = True
            continue
        if reading_expected and stripped.startswith("- "):
            val = stripped[2:].strip()
            if val and ":" not in val:
                cur_expected.append(val)
            else:
                reading_expected = False
    if cur_query is not None:
        queries.append((cur_query, cur_expected))
    return queries, threshold


def cmd_query(args) -> int:
    conn, use_vectors = _open_index(args.wiki_path, args.bm25_only)
    model = TextEmbedding(model_name=EMBED_MODEL) if use_vectors else None
    results = do_search(
        conn, args.query, args.top, use_vectors, args.alpha, args.rrf_k, model
    )
    conn.close()
    for i, (slug, title, score) in enumerate(results, 1):
        print(f"{i}. {slug} (score: {score:.4f}) -- {title}")
    return 0


def cmd_precision(args) -> int:
    queries, threshold = _parse_queries_yaml(args.queries)
    conn, use_vectors = _open_index(args.wiki_path, args.bm25_only)
    model = TextEmbedding(model_name=EMBED_MODEL) if use_vectors else None
    total_p3 = 0.0
    for query_text, expected in queries:
        results = do_search(
            conn, query_text, 3, use_vectors, args.alpha, args.rrf_k, model
        )
        actual = [r[0] for r in results]
        hits = [s for s in actual if s in expected]
        p3 = len(hits) / 3
        total_p3 += p3
        hit_str = ", ".join(hits) if hits else "(none)"
        print(f'Query: "{query_text}" — P@3: {p3:.2f} — hits: {hit_str}')
    mean_p3 = total_p3 / len(queries) if queries else 0.0
    print(f"Mean P@3: {mean_p3:.2f} (threshold: {threshold})")
    conn.close()
    return 0 if round(mean_p3, 2) >= threshold else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Search wiki index")
    sub = parser.add_subparsers(dest="command")

    qp = sub.add_parser("query", help="Run a search query")
    qp.add_argument("--wiki-path", required=True)
    qp.add_argument("--query", required=True)
    qp.add_argument("--top", type=int, default=10)
    qp.add_argument("--bm25-only", action="store_true")
    qp.add_argument("--alpha", type=float, default=0.4)
    qp.add_argument("--rrf-k", type=int, default=60)

    pp = sub.add_parser("precision", help="Validate precision against ground truth")
    pp.add_argument("--wiki-path", required=True)
    pp.add_argument("--queries", required=True)
    pp.add_argument("--bm25-only", action="store_true")
    pp.add_argument("--alpha", type=float, default=0.4)
    pp.add_argument("--rrf-k", type=int, default=60)

    args = parser.parse_args()
    if args.command == "query":
        return cmd_query(args)
    elif args.command == "precision":
        return cmd_precision(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
