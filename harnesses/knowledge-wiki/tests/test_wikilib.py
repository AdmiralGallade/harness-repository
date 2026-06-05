"""Unit tests for wikilib.py shared utilities."""

from __future__ import annotations

import struct

from wikilib import EMBED_DIM, EMBED_MODEL, _serialize_f32, body_text, parse_frontmatter


def test_constants():
    assert EMBED_MODEL == "nomic-ai/nomic-embed-text-v1.5"
    assert EMBED_DIM == 384


def test_parse_frontmatter_standard():
    text = "---\ntitle: Hello World\ntags: [a, b]\n---\nBody text."
    meta = parse_frontmatter(text)
    assert meta["title"] == "Hello World"
    assert meta["tags"] == "[a, b]"


def test_parse_frontmatter_quoted_values():
    text = '---\ntitle: "Quoted Title"\nauthor: \'Single Quoted\'\n---\n'
    meta = parse_frontmatter(text)
    assert meta["title"] == "Quoted Title"
    assert meta["author"] == "Single Quoted"


def test_parse_frontmatter_empty():
    text = "---\n---\nBody only."
    meta = parse_frontmatter(text)
    assert meta == {}


def test_parse_frontmatter_missing():
    text = "No frontmatter here.\nJust content."
    meta = parse_frontmatter(text)
    assert meta == {}


def test_parse_frontmatter_colon_in_value():
    text = "---\nurl: https://example.com\n---\n"
    meta = parse_frontmatter(text)
    assert meta["url"] == "https://example.com"


def test_parse_frontmatter_whitespace():
    text = "---\n  title :  Spaced Out  \n---\n"
    meta = parse_frontmatter(text)
    assert meta["title"] == "Spaced Out"


def test_serialize_f32_roundtrip():
    vec = [1.0, -0.5, 0.0, 3.14]
    serialized = _serialize_f32(vec)
    assert isinstance(serialized, bytes)
    assert len(serialized) == len(vec) * 4
    unpacked = list(struct.unpack(f"{len(vec)}f", serialized))
    for a, b in zip(vec, unpacked):
        assert abs(a - b) < 1e-6


def test_serialize_f32_empty():
    assert _serialize_f32([]) == b""


def test_body_text_standard():
    content = "---\ntitle: Hello\ntags: [a]\n---\nBody content here."
    assert body_text(content) == "Body content here."


def test_body_text_no_frontmatter():
    content = "Just plain text without frontmatter."
    assert body_text(content) == "Just plain text without frontmatter."


def test_body_text_empty_body():
    content = "---\ntitle: Empty\n---\n"
    assert body_text(content) == ""


def test_body_text_multiline():
    content = "---\ntitle: Multi\n---\nLine one.\n\nLine two.\n"
    assert body_text(content) == "Line one.\n\nLine two."
