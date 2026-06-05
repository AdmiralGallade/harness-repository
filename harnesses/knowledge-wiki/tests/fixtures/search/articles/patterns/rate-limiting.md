---
title: Rate Limiting Patterns
aliases: [rate limiting, throttling, API rate limits]
tags: [security, networking, performance]
tier: public
status: verified
created: 2026-02-22
---

# Rate Limiting Patterns

Rate limiting controls the number of requests a client can make within a time window. It protects services from abuse, prevents resource exhaustion, and ensures fair access across users.

## Algorithms

Token bucket: tokens are added at a fixed rate and consumed per request. Sliding window: counts requests in a rolling time window. Leaky bucket: processes requests at a fixed rate, queuing excess. Each trades off between burst tolerance and strictness.

## Implementation

Rate limits are typically enforced at the API gateway or load balancer. Redis is commonly used to track counters with atomic INCR and EXPIRE commands. Response headers (X-RateLimit-Remaining, Retry-After) communicate limits to clients.

## Distributed Rate Limiting

In multi-server deployments, rate limits must be shared across instances. Options: centralized counter (Redis), approximate local counters with periodic sync, or consistent hashing to route each client to a single counter.
