---
title: Hybrid Search vs Keyword-Only
aliases: [search strategy decision]
tags: [databases, machine-learning, architecture]
tier: public
status: verified
created: 2026-03-10
---

# Hybrid Search vs Keyword-Only

## Context

At 200+ articles, keyword-based search (grep over frontmatter) produces bunched scores that fail to distinguish relevant from irrelevant results. Semantic search alone misses exact keyword matches for technical terms.

## Decision

Use hybrid search combining BM25 (keyword) and vector similarity (semantic), merged with Reciprocal Rank Fusion. BM25 catches exact terms and identifiers. Vector search catches semantic similarity when different words express the same concept.

## Consequences

Hybrid search requires maintaining both an inverted index (FTS5) and a vector index (sqlite-vec). The build step takes longer but search quality improves significantly — score separation between relevant and irrelevant results increases from 0.01 to 0.48.
