---
title: Database Transactions
aliases: [ACID, transactions, isolation levels]
tags: [databases]
tier: public
status: verified
created: 2026-01-18
---

# Database Transactions

A transaction is a sequence of database operations that execute as a single unit. Transactions guarantee ACID properties: Atomicity (all or nothing), Consistency (valid state transitions), Isolation (concurrent transactions don't interfere), Durability (committed changes survive failures).

## Isolation Levels

SQL defines four isolation levels with increasing strictness: Read Uncommitted, Read Committed, Repeatable Read, and Serializable. Higher isolation prevents more anomalies (dirty reads, phantom reads) but reduces concurrency. Most databases default to Read Committed.

## WAL Mode in SQLite

Write-Ahead Logging (WAL) is SQLite's journal mode for concurrent access. Readers do not block writers and writers do not block readers. Changes are written to a WAL file first, then checkpointed to the main database. WAL enables much better concurrency than the default rollback journal.

## Deadlock Detection

When two transactions each hold a lock the other needs, a deadlock occurs. Databases detect deadlocks by analyzing the wait-for graph and abort one transaction. Applications should handle deadlocks by retrying the aborted transaction.
