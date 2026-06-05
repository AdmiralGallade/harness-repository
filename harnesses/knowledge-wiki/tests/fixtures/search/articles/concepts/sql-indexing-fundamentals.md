---
title: SQL Indexing Fundamentals
aliases: [database indexes, B-tree indexes]
tags: [databases, performance]
tier: public
status: verified
created: 2026-01-15
---

# SQL Indexing Fundamentals

Database indexes are data structures that improve the speed of data retrieval operations. The most common type is the B-tree index, which maintains sorted data and allows searches, insertions, and deletions in logarithmic time.

## How B-tree Indexes Work

A B-tree index stores key-value pairs in a balanced tree structure. Each node contains multiple keys and child pointers. When a query searches for a value, the database engine traverses the tree from root to leaf, comparing keys at each level.

## When to Use Indexes

Create indexes on columns frequently used in WHERE clauses, JOIN conditions, and ORDER BY clauses. Avoid over-indexing — each index adds overhead to INSERT and UPDATE operations. A table with too many indexes can become slower for write-heavy workloads.

## Composite Indexes

Composite indexes span multiple columns. The column order matters — the index is most effective when queries filter on the leftmost columns first. This is known as the leftmost prefix rule.
