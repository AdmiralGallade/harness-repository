---
title: Load Balancing
aliases: [load balancer, traffic distribution]
tags: [networking, performance]
tier: public
status: verified
created: 2026-01-28
---

# Load Balancing

Load balancing distributes incoming network traffic across multiple servers to ensure no single server is overwhelmed. It improves availability, reliability, and response times.

## Algorithms

Round-robin: rotates through servers sequentially. Least connections: sends to the server with fewest active connections. Weighted: assigns capacity proportional to server capability. Consistent hashing: maps requests to servers based on a hash function, useful for stateful sessions.

## Layer 4 vs Layer 7

Layer 4 (transport) load balancers route based on IP and port — fast but no application awareness. Layer 7 (application) load balancers inspect HTTP headers, URLs, and content — enabling path-based routing, header manipulation, and SSL termination.

## Health Checks

Load balancers periodically probe servers to detect failures. Active checks send requests and verify responses. Passive checks monitor live traffic for errors. Unhealthy servers are removed from the pool and reinstated after recovery.
