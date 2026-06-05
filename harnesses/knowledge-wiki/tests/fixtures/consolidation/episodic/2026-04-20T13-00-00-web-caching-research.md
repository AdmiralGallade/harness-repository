---
timestamp: 2026-04-20T13:00:00Z
worker: claude-code
task_id: research-caching-002
tags: [performance, architecture]
wiki: test-consolidation
---

# Web Caching Research Findings

CDN caching is the first layer of defense for web application performance. Content Delivery Networks like CloudFront and Fastly cache static assets at edge locations close to users, reducing origin server load and improving latency. CDN cache behavior is controlled through HTTP cache headers such as Cache-Control and ETag, and cache invalidation is typically handled through TTL expiration or explicit purge requests. For dynamic content, CDN edge computing can cache API responses with short TTLs to balance freshness with performance.

Application-level caching using Redis or Memcached provides sub-millisecond access to frequently requested data. Redis is preferred for structured data caching due to its support for data types like sorted sets, hashes, and lists, while Memcached excels at simple key-value caching with lower memory overhead per key. Common patterns include cache-aside (lazy loading), where the application checks the cache before querying the database, and write-through caching, where writes go to both the cache and database simultaneously to maintain consistency.

Browser caching leverages HTTP cache headers to store responses locally on the client. The Cache-Control header with max-age directives tells the browser how long to cache a resource, while ETag and Last-Modified headers enable conditional requests for revalidation. Proper browser cache configuration can reduce repeat page load times by 60-80%.

Cache invalidation remains one of the hardest problems in distributed systems. TTL-based invalidation is the simplest approach, where cached entries expire after a fixed duration, but it trades freshness for simplicity. Event-based invalidation uses pub/sub mechanisms to notify caches when source data changes, providing near-real-time consistency. Write-through and write-behind patterns ensure cache consistency by updating the cache as part of the write path, with write-behind deferring the database write for better write performance.
