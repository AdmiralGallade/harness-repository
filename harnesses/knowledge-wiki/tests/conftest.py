"""Shared fixtures and import validation for knowledge-wiki test suite."""

from __future__ import annotations

import os
import shutil

import pytest

import wikilib
import indexer
import search
import consolidate

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def search_wiki_path() -> str:
    return os.path.join(FIXTURES_DIR, "search")


@pytest.fixture
def consolidation_wiki_path() -> str:
    return os.path.join(FIXTURES_DIR, "consolidation")



def build_test_index(tmp_path, src_wiki: str, no_vectors: bool = True) -> str:
    """Copy a fixture wiki to tmp_path and build a fresh search index."""
    dest = str(tmp_path / "wiki")
    shutil.copytree(src_wiki, dest, ignore=shutil.ignore_patterns(".wiki-index.db"))
    indexer.build_index(dest, rebuild=True, no_vectors=no_vectors)
    return dest
