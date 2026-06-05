---
title: "API Rate Limiting Patterns"
aliases: [rate limiting, throttling]
category: patterns
tags: [security, architecture]
parents: []
created: 2026-04-15
updated: 2026-04-15
tier: public
status: reviewed
---

# API Rate Limiting Patterns

Rate limiting is a critical mechanism for protecting APIs from abuse, ensuring fair resource allocation, and maintaining service stability. The token bucket algorithm is one of the most widely used approaches: a bucket holds a fixed number of tokens that are replenished at a constant rate, and each API request consumes one token. When the bucket is empty, requests are rejected or queued. Token bucket naturally allows short bursts of traffic while enforcing an average rate over time, making it suitable for most API use cases.

The sliding window algorithm provides smoother rate limiting by tracking requests within a continuously moving time window. Unlike fixed window approaches that can allow double the rate at window boundaries, sliding window counts requests across the boundary by weighting the previous window's count proportionally. For example, if the window is 60 seconds and we are 25% into the current window, the effective count is 75% of the previous window's count plus 100% of the current window's count. This prevents the burst problem inherent in fixed window counters.

Fixed window rate limiting divides time into discrete intervals and counts requests within each interval. It is the simplest approach to implement — typically requiring only an atomic counter with a TTL in Redis or a similar store. The main drawback is the boundary condition: a client could make the maximum number of requests at the end of one window and again at the start of the next, effectively doubling the intended rate for a brief period. Despite this limitation, fixed window is sufficient for many applications where exact rate enforcement is not critical.

Rate limit responses should follow HTTP conventions by returning a 429 Too Many Requests status code with Retry-After and X-RateLimit-Remaining headers. These headers enable well-behaved clients to self-throttle and implement exponential backoff. Rate limiting metadata should also be included in successful responses so clients can proactively adjust their request rates before hitting limits.
