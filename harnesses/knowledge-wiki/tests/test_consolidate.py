"""Unit and integration tests for consolidate.py."""

from __future__ import annotations

import json
import os
import shutil

import pytest

from conftest import build_test_index
from wikilib import body_text
from consolidate import (
    crawl_episodic,
    do_mark,
    do_scan,
    find_best_match,
    load_threshold,
    main,
    open_index,
    parse_tags,
    read_consolidated,
    _cosine_sim,
    DEFAULT_THRESHOLD,
)


def test_parse_tags_standard():
    text = "---\ntags: [python, testing, ci]\n---\nBody."
    tags = parse_tags(text)
    assert "python" in tags
    assert "testing" in tags
    assert "ci" in tags


def test_parse_tags_empty():
    text = "---\ntitle: No tags\n---\nBody."
    assert parse_tags(text) == []


def test_parse_tags_no_frontmatter():
    assert parse_tags("Just text.") == []


def test_body_text_standard():
    text = "---\ntitle: Test\n---\nThe body content."
    assert body_text(text) == "The body content."


def test_body_text_no_frontmatter():
    text = "Just plain text."
    assert body_text(text) == "Just plain text."


def test_body_text_multiline():
    text = "---\ntitle: T\n---\nLine 1.\n\nLine 2."
    assert body_text(text) == "Line 1.\n\nLine 2."


def test_cosine_sim_identical():
    v = [1.0, 0.0, 0.5]
    assert abs(_cosine_sim(v, v) - 1.0) < 1e-6


def test_cosine_sim_orthogonal():
    assert abs(_cosine_sim([1.0, 0.0], [0.0, 1.0])) < 1e-6


def test_cosine_sim_zero_vector():
    assert _cosine_sim([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_find_best_match_basic():
    embeddings = [("a", [1.0, 0.0]), ("b", [0.0, 1.0])]
    result = find_best_match(embeddings, [0.9, 0.1])
    assert result is not None
    slug, score = result
    assert slug == "a"
    assert score > 0.5


def test_find_best_match_empty():
    assert find_best_match([], [1.0, 0.0]) is None


def test_read_consolidated_missing(tmp_path):
    assert read_consolidated(str(tmp_path)) == set()


def test_read_consolidated_existing(tmp_path):
    ep = tmp_path / "episodic"
    ep.mkdir()
    (ep / ".consolidated").write_text("a.md\nb.md\n")
    result = read_consolidated(str(tmp_path))
    assert result == {"a.md", "b.md"}


def test_crawl_episodic(consolidation_wiki_path):
    entries = crawl_episodic(consolidation_wiki_path)
    assert len(entries) >= 5
    assert all(e.endswith(".md") for e in entries)


def test_crawl_episodic_empty(tmp_path):
    assert crawl_episodic(str(tmp_path)) == []


def test_load_threshold_default(tmp_path):
    assert load_threshold(str(tmp_path), None) == DEFAULT_THRESHOLD


def test_load_threshold_override():
    assert load_threshold("/nonexistent", 0.9) == 0.9


def test_do_scan_no_vectors(tmp_path, consolidation_wiki_path, monkeypatch):
    wiki = build_test_index(tmp_path, consolidation_wiki_path)
    import io
    buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", buf)
    do_scan(wiki, threshold_override=None)
    result = json.loads(buf.getvalue())
    assert "candidates" in result
    assert "high_similarity" in result
    assert result["total_scanned"] >= 5


def test_do_scan_empty_episodic(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    (wiki / "articles").mkdir(parents=True)
    import io
    buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", buf)
    do_scan(str(wiki), threshold_override=None)
    result = json.loads(buf.getvalue())
    assert result["candidates"] == []
    assert result["total_scanned"] == 0


def test_do_mark(tmp_path):
    ep = tmp_path / "episodic"
    ep.mkdir()
    entry = "test-entry.md"
    (ep / entry).write_text("---\ntimestamp: 2026-01-01\nworker: test\n---\nSome content here.")
    do_mark(str(tmp_path), entry, "extracted", facts=3, inbox_entries_str="inbox-a.md,inbox-b.md")
    content = (ep / entry).read_text()
    assert "consolidated_at:" in content
    assert "consolidation_result: extracted" in content
    assert "facts_extracted: 3" in content
    assert "inbox_entries:" in content
    assert "Some content here." in content
    marker = (ep / ".consolidated").read_text()
    assert entry in marker


def test_open_index_missing(tmp_path):
    conn, use_vectors = open_index(str(tmp_path))
    assert conn is None
    assert use_vectors is False


def test_open_index_no_vectors(tmp_path, consolidation_wiki_path):
    wiki = build_test_index(tmp_path, consolidation_wiki_path)
    conn, use_vectors = open_index(wiki)
    assert conn is not None
    assert use_vectors is False
    conn.close()


def test_do_scan_all_consolidated(tmp_path, monkeypatch):
    wiki = tmp_path / "wiki"
    ep = wiki / "episodic"
    ep.mkdir(parents=True)
    (wiki / "articles").mkdir()
    (ep / "a.md").write_text("---\ntimestamp: 2026-01-01\n---\nA.")
    (ep / ".consolidated").write_text("a.md\n")
    import io
    buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", buf)
    do_scan(str(wiki), threshold_override=None)
    result = json.loads(buf.getvalue())
    assert result["candidates"] == []
    assert result["already_processed"] == 1


def test_do_mark_missing_entry(tmp_path):
    ep = tmp_path / "episodic"
    ep.mkdir()
    with pytest.raises(SystemExit):
        do_mark(str(tmp_path), "nonexistent.md", "extracted", 0, "")


def test_do_mark_no_frontmatter(tmp_path):
    ep = tmp_path / "episodic"
    ep.mkdir()
    (ep / "bad.md").write_text("No frontmatter here.")
    with pytest.raises(SystemExit):
        do_mark(str(tmp_path), "bad.md", "extracted", 0, "")


def test_main_scan(tmp_path, consolidation_wiki_path, monkeypatch):
    wiki = build_test_index(tmp_path, consolidation_wiki_path)
    monkeypatch.setattr("sys.argv", ["consolidate.py", "scan", "--wiki-path", wiki])
    main()


def test_main_no_args(monkeypatch):
    monkeypatch.setattr("sys.argv", ["consolidate.py"])
    with pytest.raises(SystemExit):
        main()


def test_do_mark_preserves_body(tmp_path):
    ep = tmp_path / "episodic"
    ep.mkdir()
    entry = "body-test.md"
    body = "Line 1.\n\n## Section\n\nLine 2 with special chars: <>&\n"
    (ep / entry).write_text(f"---\ntimestamp: 2026-01-01\n---\n{body}")
    do_mark(str(tmp_path), entry, "duplicate", facts=0, inbox_entries_str="")
    content = (ep / entry).read_text()
    assert body in content
