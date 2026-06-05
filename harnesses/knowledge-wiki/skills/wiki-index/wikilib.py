#!/usr/bin/env python3
"""Shared constants and utilities for wiki search and consolidation scripts."""

from __future__ import annotations

import re
import struct

try:
    from fastembed import TextEmbedding
    import sqlite_vec

    _HAS_VECTORS = True
except ImportError:
    _HAS_VECTORS = False

EMBED_MODEL = "nomic-ai/nomic-embed-text-v1.5"
EMBED_DIM = 384


def _serialize_f32(vec: list[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def body_text(content: str) -> str:
    m = re.match(r"^---\n.*?\n---\n?", content, re.DOTALL)
    return content[m.end():].strip() if m else content.strip()


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
