---
title: Connection Pooling
aliases: [database connection pool, pool management]
tags: [databases, performance]
tier: public
status: verified
created: 2026-02-20
---

# Connection Pooling

Connection pooling reuses database connections across requests instead of creating a new connection for each query. This eliminates the overhead of TCP handshakes, TLS negotiation, and authentication for every database operation.

## Pool Configuration

Key parameters: minimum idle connections (keep warm), maximum pool size (prevent overload), connection timeout (fail fast), idle timeout (reclaim unused). PgBouncer and HikariCP are widely used pool implementations for PostgreSQL and Java respectively.

## Connection Lifecycle

A connection is acquired from the pool, used for queries, then returned. Health checks verify connections are still valid before reuse. Stale connections are evicted and replaced. The pool handles reconnection transparently after network failures.
