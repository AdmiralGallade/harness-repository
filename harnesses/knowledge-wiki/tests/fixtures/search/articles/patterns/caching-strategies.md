---
title: Caching Strategies
aliases: [cache, caching, cache invalidation]
tags: [performance, databases]
tier: public
status: verified
created: 2026-02-25
---

# Caching Strategies

Caching stores frequently accessed data in a faster storage layer to reduce latency and load on the primary data store. The key challenge is cache invalidation — ensuring cached data stays consistent with the source of truth.

## Cache-Aside (Lazy Loading)

The application checks the cache first. On a miss, it reads from the database, stores the result in cache, and returns it. Simple to implement but can cause cache stampedes when many requests miss simultaneously.

## Write-Through and Write-Behind

Write-through updates the cache and database synchronously on every write. Write-behind (write-back) updates the cache immediately and asynchronously writes to the database. Write-behind improves write performance but risks data loss on cache failure.

## Eviction Policies

When the cache is full, eviction policies decide what to remove. LRU (Least Recently Used) is the most common. LFU (Least Frequently Used) keeps popular items longer. TTL-based expiration removes items after a fixed time regardless of access pattern.
