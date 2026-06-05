---
title: Full-Text Search Engines
aliases: [FTS, text search, search engines]
tags: [databases, performance]
tier: public
status: verified
created: 2026-01-20
---

# Full-Text Search Engines

Full-text search enables finding documents by their content rather than exact field matches. Unlike SQL LIKE queries, full-text search uses inverted indexes that map terms to the documents containing them.

## BM25 Ranking

BM25 (Best Matching 25) is the standard ranking function for full-text search. It scores documents based on term frequency (how often the term appears in the document) and inverse document frequency (how rare the term is across all documents). BM25 also applies length normalization so shorter documents are not penalized.

## SQLite FTS5

SQLite's FTS5 extension provides full-text search with BM25 ranking built in. It creates a virtual table backed by an inverted index. Queries use the MATCH operator and results are ranked by relevance automatically.

## Elasticsearch and Alternatives

For larger deployments, dedicated search engines like Elasticsearch, Typesense, and Meilisearch provide distributed full-text search with additional features like fuzzy matching, faceted search, and real-time indexing.
