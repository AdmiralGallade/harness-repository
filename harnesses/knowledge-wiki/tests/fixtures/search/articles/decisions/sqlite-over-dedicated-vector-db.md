---
title: SQLite Over Dedicated Vector Database
aliases: [vector DB choice, sqlite-vec decision]
tags: [databases, architecture]
tier: public
status: verified
created: 2026-03-12
---

# SQLite Over Dedicated Vector Database

## Context

Needed vector search capability for wiki retrieval. Options evaluated: Pinecone (hosted), Qdrant (self-hosted), LanceDB (embedded), sqlite-vec (SQLite extension).

## Decision

Use sqlite-vec as an extension to the existing SQLite database rather than introducing a separate vector store. SQLite is already a system library, FTS5 provides BM25 search, and sqlite-vec adds vector capability to the same database file.

## Consequences

Single database file contains both text and vector indexes. No additional infrastructure or processes to manage. Trade-off: sqlite-vec is less mature than dedicated vector databases and lacks features like HNSW indexing for very large collections. Acceptable for wikis under 10,000 articles.
