"""Unit and integration tests for search.py."""

from __future__ import annotations

import os
import sqlite3

import pytest

import argparse
import shutil

from conftest import build_test_index
from search import _sanitize_fts, _open_index, _query_bm25, _rrf_fuse, do_search, _parse_queries_yaml, cmd_query, cmd_precision, main
from wikilib import _HAS_VECTORS


def test_sanitize_fts_basic():
    assert _sanitize_fts("hello world") == "hello OR world"


def test_sanitize_fts_special_chars():
    assert _sanitize_fts('find "exact" match!') == "find OR exact OR match"


def test_sanitize_fts_single_char_dropped():
    result = _sanitize_fts("a test b query")
    assert "a" not in result.split(" OR ")
    assert "b" not in result.split(" OR ")
    assert "test" in result
    assert "query" in result


def test_sanitize_fts_empty():
    assert _sanitize_fts("") == ""


def test_rrf_fuse_basic():
    bm25 = [("a", "Article A"), ("b", "Article B"), ("c", "Article C")]
    vec = [("b", "Article B"), ("a", "Article A"), ("d", "Article D")]
    fused = _rrf_fuse(bm25, vec, alpha=0.4, k=60, top_n=3)
    slugs = [s for s, _, _ in fused]
    assert "a" in slugs
    assert "b" in slugs
    assert len(fused) <= 3
    for _, _, score in fused:
        assert score > 0


def test_rrf_fuse_bm25_only():
    bm25 = [("x", "X"), ("y", "Y")]
    fused = _rrf_fuse(bm25, [], alpha=0.4, k=60, top_n=5)
    assert len(fused) == 2
    assert fused[0][0] == "x"


def test_rrf_fuse_disjoint():
    bm25 = [("a", "A")]
    vec = [("b", "B")]
    fused = _rrf_fuse(bm25, vec, alpha=0.5, k=60, top_n=5)
    slugs = {s for s, _, _ in fused}
    assert slugs == {"a", "b"}


def test_do_search_integration(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    results = do_search(conn, "database", top_n=5, use_vectors=False, alpha=0.4, rrf_k=60)
    conn.close()
    assert len(results) > 0
    assert all(len(r) == 3 for r in results)


def test_do_search_returns_ranked(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    results = do_search(conn, "testing", top_n=3, use_vectors=False, alpha=0.4, rrf_k=60)
    conn.close()
    scores = [r[2] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_parse_queries_yaml(search_wiki_path):
    yaml_path = os.path.join(search_wiki_path, "queries.yaml")
    queries, threshold = _parse_queries_yaml(yaml_path)
    assert len(queries) >= 5
    assert threshold > 0
    for query_text, expected in queries:
        assert isinstance(query_text, str)
        assert isinstance(expected, list)
        assert len(expected) > 0


def test_open_index_bm25_only(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    conn, use_vectors = _open_index(wiki, bm25_only=True)
    assert conn is not None
    assert use_vectors is False
    conn.close()


def test_open_index_missing(tmp_path):
    with pytest.raises(SystemExit):
        _open_index(str(tmp_path))


def test_query_bm25(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    results = _query_bm25(conn, "database", 5)
    conn.close()
    assert len(results) > 0
    assert all(len(r) == 2 for r in results)


def test_cmd_query(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    args = argparse.Namespace(
        wiki_path=wiki, query="database", top=5, bm25_only=True, alpha=0.4, rrf_k=60
    )
    assert cmd_query(args) == 0


def test_cmd_precision(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    queries_src = os.path.join(search_wiki_path, "queries.yaml")
    queries_dst = os.path.join(wiki, "queries.yaml")
    shutil.copy2(queries_src, queries_dst)
    args = argparse.Namespace(
        wiki_path=wiki, queries=queries_dst, bm25_only=True, alpha=0.4, rrf_k=60
    )
    cmd_precision(args)


def test_main_no_args(monkeypatch):
    monkeypatch.setattr("sys.argv", ["search.py"])
    assert main() == 1


@pytest.mark.skipif(not _HAS_VECTORS, reason="fastembed/sqlite-vec not available")
def test_do_search_with_vectors(tmp_path, search_wiki_path):
    from indexer import build_index
    import shutil

    dest = str(tmp_path / "wiki")
    shutil.copytree(search_wiki_path, dest, ignore=shutil.ignore_patterns(".wiki-index.db"))
    build_index(dest, rebuild=True, no_vectors=False)
    db_path = os.path.join(dest, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    from fastembed import TextEmbedding
    from wikilib import EMBED_MODEL
    import sqlite_vec

    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    model = TextEmbedding(model_name=EMBED_MODEL)
    results = do_search(conn, "database", top_n=5, use_vectors=True, alpha=0.4, rrf_k=60, embed_model=model)
    conn.close()
    assert len(results) > 0
