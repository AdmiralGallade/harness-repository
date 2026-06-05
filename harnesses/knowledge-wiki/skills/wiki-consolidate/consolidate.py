#!/usr/bin/env python3
"""Consolidation pipeline: scan episodic entries for dedup, mark processed entries."""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import struct
import sys
from datetime import datetime, timezone

# Import shared utilities from wikilib (in wiki-index/). Falls back to inline
# definitions for standalone deployment where wikilib is not on sys.path.
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wiki-index"))
    from wikilib import EMBED_MODEL, EMBED_DIM, _HAS_VECTORS, _serialize_f32, parse_frontmatter, body_text
except ImportError:
    EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
    EMBED_DIM = 384
    def _serialize_f32(vec: list[float]) -> bytes:
        return struct.pack(f"{len(vec)}f", *vec)
    def parse_frontmatter(text: str) -> dict[str, str]:
        m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
        if not m:
            return {}
        meta = {}
        for line in m.group(1).splitlines():
            key, sep, val = line.partition(":")
            if not sep:
                continue
            key = key.strip()
            val = val.strip().strip("\"'")
            meta[key] = val
        return meta
    def body_text(content: str) -> str:
        m = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
        return content[m.end():].strip() if m else content.strip()
    try:
        from fastembed import TextEmbedding
        import sqlite_vec
        _HAS_VECTORS = True
    except ImportError:
        _HAS_VECTORS = False

if _HAS_VECTORS:
    from fastembed import TextEmbedding
    import sqlite_vec

DEFAULT_THRESHOLD = 0.85


def parse_tags(text: str) -> list[str]:
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return []
    for line in m.group(1).splitlines():
        key, sep, val = line.partition(":")
        if not sep:
            continue
        if key.strip() == "tags":
            return [t.strip().strip("\"'") for t in re.findall(r"[\w-]+", val)]
    return []


def read_consolidated(wiki_path: str) -> set[str]:
    marker = os.path.join(wiki_path, "episodic", ".consolidated")
    if not os.path.exists(marker):
        return set()
    with open(marker, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def crawl_episodic(wiki_path: str) -> list[str]:
    ep_dir = os.path.join(wiki_path, "episodic")
    if not os.path.isdir(ep_dir):
        return []
    return sorted(
        fn
        for fn in os.listdir(ep_dir)
        if fn.endswith(".md") and not fn.startswith(".")
    )


def load_threshold(wiki_path: str, override: float | None) -> float:
    if override is not None:
        return override
    wikis_json = os.path.expanduser("~/.claude/wikis.json")
    if os.path.exists(wikis_json):
        with open(wikis_json, encoding="utf-8") as f:
            data = json.load(f)
        real_path = os.path.realpath(wiki_path)
        for w in data.get("wikis", []):
            if os.path.realpath(w.get("path", "")) == real_path:
                cfg = w.get("consolidation", {})
                return cfg.get("dedup_cosine_threshold", DEFAULT_THRESHOLD)
    return DEFAULT_THRESHOLD


def open_index(wiki_path: str) -> tuple[sqlite3.Connection | None, bool]:
    db_path = os.path.join(wiki_path, ".wiki-index.db")
    if not os.path.exists(db_path):
        return None, False
    conn = sqlite3.connect(db_path)
    use_vectors = False
    if _HAS_VECTORS:
        row = conn.execute(
            "SELECT value FROM meta WHERE key = 'has_vectors'"
        ).fetchone()
        if row and row[0] == "true":
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            use_vectors = True
    return conn, use_vectors


def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def load_article_embeddings(
    conn: sqlite3.Connection,
) -> list[tuple[str, list[float]]]:
    article_ids = conn.execute(
        "SELECT id, slug FROM articles WHERE path LIKE 'articles/%'"
    ).fetchall()
    result = []
    for aid, slug in article_ids:
        row = conn.execute(
            "SELECT embedding FROM articles_vec WHERE id = ?", (aid,)
        ).fetchone()
        if row and row[0]:
            vec = list(struct.unpack(f"{EMBED_DIM}f", row[0]))
            result.append((slug, vec))
    return result


def find_best_match(
    article_embeddings: list[tuple[str, list[float]]],
    query_vec: list[float],
) -> tuple[str, float] | None:
    best_slug = None
    best_sim = -1.0
    for slug, emb in article_embeddings:
        sim = _cosine_sim(query_vec, emb)
        if sim > best_sim:
            best_sim = sim
            best_slug = slug
    if best_slug is None:
        return None
    return best_slug, best_sim


def do_scan(wiki_path: str, threshold_override: float | None) -> None:
    wiki_path = os.path.abspath(wiki_path)
    threshold = load_threshold(wiki_path, threshold_override)

    all_entries = crawl_episodic(wiki_path)
    if not all_entries:
        json.dump(
            {
                "wiki_path": wiki_path,
                "threshold": threshold,
                "vectors_available": False,
                "candidates": [],
                "high_similarity": [],
                "already_processed": 0,
                "total_scanned": 0,
            },
            sys.stdout,
            indent=2,
        )
        return

    already = read_consolidated(wiki_path)
    unconsolidated = [e for e in all_entries if e not in already]

    if not unconsolidated:
        json.dump(
            {
                "wiki_path": wiki_path,
                "threshold": threshold,
                "vectors_available": False,
                "candidates": [],
                "high_similarity": [],
                "already_processed": len(already),
                "total_scanned": len(all_entries),
            },
            sys.stdout,
            indent=2,
        )
        return

    conn, use_vectors = open_index(wiki_path)
    if conn is None:
        print("Warning: No search index found. Classifying all as candidate.", file=sys.stderr)

    embed_model = None
    article_embeddings: list[tuple[str, list[float]]] = []
    if use_vectors and _HAS_VECTORS and conn is not None:
        embed_model = TextEmbedding(EMBED_MODEL)
        article_embeddings = load_article_embeddings(conn)

    candidates = []
    high_similarity = []
    ep_dir = os.path.join(wiki_path, "episodic")

    for entry_fn in unconsolidated:
        fpath = os.path.join(ep_dir, entry_fn)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        tags = parse_tags(content)
        body = body_text(content)

        if not use_vectors or embed_model is None or not article_embeddings:
            candidates.append({"entry": entry_fn, "tags": tags})
            continue

        emb = list(embed_model.embed([body]))[0][: EMBED_DIM]
        match = find_best_match(article_embeddings, list(emb))

        if match and match[1] >= threshold:
            slug, score = match
            high_similarity.append(
                {
                    "entry": entry_fn,
                    "matched_slug": slug,
                    "score": round(score, 4),
                    "tags": tags,
                }
            )
        else:
            candidates.append({"entry": entry_fn, "tags": tags})

    if conn:
        conn.close()

    json.dump(
        {
            "wiki_path": wiki_path,
            "threshold": threshold,
            "vectors_available": use_vectors,
            "candidates": candidates,
            "high_similarity": high_similarity,
            "already_processed": len(already),
            "total_scanned": len(all_entries),
        },
        sys.stdout,
        indent=2,
    )


def do_mark(
    wiki_path: str,
    entry: str,
    result: str,
    facts: int,
    inbox_entries_str: str,
) -> None:
    wiki_path = os.path.abspath(wiki_path)
    ep_dir = os.path.join(wiki_path, "episodic")
    fpath = os.path.join(ep_dir, entry)

    if not os.path.exists(fpath):
        print(f"Error: {fpath} not found", file=sys.stderr)
        sys.exit(1)

    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    m = re.match(r"^(---\n)(.*?)(\n---\n)", content, re.DOTALL)
    if not m:
        print(f"Error: No frontmatter in {entry}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    inbox_list = [x.strip() for x in inbox_entries_str.split(",") if x.strip()] if inbox_entries_str else []
    inbox_yaml = "[" + ", ".join(inbox_list) + "]" if inbox_list else "[]"

    new_fields = (
        f"consolidated_at: {now}\n"
        f"consolidation_result: {result}\n"
        f"facts_extracted: {facts}\n"
        f"inbox_entries: {inbox_yaml}\n"
    )

    new_content = m.group(1) + m.group(2) + "\n" + new_fields + m.group(3) + content[m.end() :]

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)

    marker = os.path.join(ep_dir, ".consolidated")
    existing = set()
    if os.path.exists(marker):
        with open(marker, encoding="utf-8") as f:
            existing = {line.strip() for line in f if line.strip()}
    existing.add(entry)
    with open(marker, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(existing)) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Consolidation pipeline")
    sub = parser.add_subparsers(dest="command")

    scan_p = sub.add_parser("scan", help="Scan episodic entries for dedup classification")
    scan_p.add_argument("--wiki-path", required=True)
    scan_p.add_argument("--threshold", type=float, default=None)

    mark_p = sub.add_parser("mark", help="Mark an episodic entry as consolidated")
    mark_p.add_argument("--wiki-path", required=True)
    mark_p.add_argument("--entry", required=True)
    mark_p.add_argument("--result", required=True, choices=["extracted", "duplicate", "low-confidence"])
    mark_p.add_argument("--facts", type=int, default=0)
    mark_p.add_argument("--inbox-entries", default="")

    args = parser.parse_args()

    if args.command == "scan":
        do_scan(args.wiki_path, args.threshold)
    elif args.command == "mark":
        do_mark(args.wiki_path, args.entry, args.result, args.facts, args.inbox_entries)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
