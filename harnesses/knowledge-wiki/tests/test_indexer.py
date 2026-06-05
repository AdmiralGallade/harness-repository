"""Unit and integration tests for indexer.py."""

from __future__ import annotations

import os
import sqlite3

import pytest

from conftest import build_test_index
from indexer import Article, crawl_wiki, delete_stale, init_db, main, parse_article, build_index, get_existing_hashes, update_meta, upsert_article


@pytest.fixture
def mini_wiki(tmp_path):
    """Create a minimal wiki with 2 articles for unit tests."""
    articles = tmp_path / "articles" / "concepts"
    articles.mkdir(parents=True)
    (articles / "alpha.md").write_text(
        "---\ntitle: Alpha\ntier: public\nupdated: 2026-01-01\n---\nAlpha content."
    )
    (articles / "beta.md").write_text(
        "---\ntitle: Beta\ntier: private\ncreated: 2026-02-01\n---\nBeta content."
    )
    episodic = tmp_path / "episodic"
    episodic.mkdir()
    (episodic / "entry.md").write_text(
        "---\ntimestamp: 2026-03-01\n---\nEpisodic entry."
    )
    return str(tmp_path)


def test_parse_article_fields(mini_wiki):
    fpath = os.path.join(mini_wiki, "articles", "concepts", "alpha.md")
    a = parse_article(fpath, mini_wiki)
    assert a.slug == "alpha"
    assert a.title == "Alpha"
    assert a.tier == "public"
    assert a.updated_at == "2026-01-01"
    assert a.content_hash
    assert "articles/concepts/alpha.md" in a.path


def test_parse_article_fallback_title(mini_wiki):
    fpath = os.path.join(mini_wiki, "episodic", "entry.md")
    a = parse_article(fpath, mini_wiki)
    assert a.slug == "entry"
    assert a.title == "Entry"
    assert a.updated_at == "2026-03-01"


def test_crawl_wiki(mini_wiki):
    paths = crawl_wiki(mini_wiki)
    basenames = [os.path.basename(p) for p in paths]
    assert "alpha.md" in basenames
    assert "beta.md" in basenames
    assert "entry.md" in basenames
    assert len(paths) == 3


def test_crawl_wiki_empty(tmp_path):
    (tmp_path / "articles").mkdir()
    assert crawl_wiki(str(tmp_path)) == []


def test_init_db_schema(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = init_db(db_path, rebuild=False, use_vectors=False)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "articles" in tables
    assert "articles_fts" in tables
    assert "meta" in tables
    conn.close()


def test_build_index_from_fixtures(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    assert os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    assert count >= 20
    conn.close()


def test_build_index_incremental(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    count1 = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    build_index(wiki, rebuild=False, no_vectors=True)
    conn = sqlite3.connect(db_path)
    count2 = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    assert count1 == count2


def test_build_index_rebuild_idempotent(tmp_path, search_wiki_path):
    wiki = build_test_index(tmp_path, search_wiki_path)
    db_path = os.path.join(wiki, ".wiki-index.db")
    conn = sqlite3.connect(db_path)
    count1 = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    build_index(wiki, rebuild=True, no_vectors=True)
    conn = sqlite3.connect(db_path)
    count2 = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    assert count1 == count2


def test_upsert_article_insert_and_update(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = init_db(db_path)
    a = Article(slug="test", path="articles/test.md", title="Test", content="Body",
                content_hash="abc", tier="public", updated_at="2026-01-01")
    upsert_article(conn, a, exists=False)
    conn.commit()
    row = conn.execute("SELECT title FROM articles WHERE slug='test'").fetchone()
    assert row[0] == "Test"
    a2 = Article(slug="test", path="articles/test.md", title="Updated", content="New",
                 content_hash="def", tier="public", updated_at="2026-02-01")
    upsert_article(conn, a2, exists=True)
    conn.commit()
    row = conn.execute("SELECT title FROM articles WHERE slug='test'").fetchone()
    assert row[0] == "Updated"
    conn.close()


def test_delete_stale(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = init_db(db_path)
    a = Article(slug="old", path="articles/old.md", title="Old", content="Body",
                content_hash="xyz", tier=None, updated_at="")
    upsert_article(conn, a, exists=False)
    conn.commit()
    assert conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == 1
    delete_stale(conn, {"old"})
    conn.commit()
    assert conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0] == 0
    conn.close()


def test_update_meta(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = init_db(db_path)
    a = Article(slug="m", path="p", title="T", content="C", content_hash="h", tier=None, updated_at="")
    upsert_article(conn, a, exists=False)
    conn.commit()
    count = update_meta(conn, has_vectors=False)
    assert count == 1
    version = conn.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0]
    assert version == "1"
    conn.close()


def test_build_index_detects_update(tmp_path):
    articles = tmp_path / "wiki" / "articles" / "concepts"
    articles.mkdir(parents=True)
    wiki = str(tmp_path / "wiki")
    (articles / "doc.md").write_text("---\ntitle: V1\n---\nOriginal.")
    build_index(wiki, rebuild=True, no_vectors=True)
    (articles / "doc.md").write_text("---\ntitle: V2\n---\nUpdated content.")
    build_index(wiki, rebuild=False, no_vectors=True)
    conn = sqlite3.connect(os.path.join(wiki, ".wiki-index.db"))
    title = conn.execute("SELECT title FROM articles WHERE slug='doc'").fetchone()[0]
    conn.close()
    assert title == "V2"


def test_main_no_args(monkeypatch):
    monkeypatch.setattr("sys.argv", ["indexer.py"])
    assert main() == 1


def test_main_build(tmp_path, mini_wiki, monkeypatch):
    monkeypatch.setattr("sys.argv", ["indexer.py", "build", "--wiki-path", mini_wiki, "--no-vectors"])
    assert main() == 0
    assert os.path.exists(os.path.join(mini_wiki, ".wiki-index.db"))


def test_main_missing_articles(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.argv", ["indexer.py", "build", "--wiki-path", str(tmp_path)])
    assert main() == 1
