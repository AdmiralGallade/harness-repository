---
timestamp: 2026-04-20T10:00:00Z
worker: claude-code
task_id: research-observability-001
tags: [testing, deployment]
wiki: test-consolidation
---

# Microservice Observability Research

Distributed tracing is essential for understanding request flow across microservice boundaries. OpenTelemetry has emerged as the standard instrumentation framework, providing vendor-neutral APIs for traces, metrics, and logs. Traces consist of spans that represent individual operations, linked by trace IDs and parent-child relationships. Jaeger and Zipkin are the most common trace collection backends, with Jaeger being preferred for its native OpenTelemetry support and adaptive sampling capabilities.

Structured logging in microservices requires correlation IDs propagated through request headers to tie log entries across services to a single user request. JSON-formatted logs with standardized fields (timestamp, service_name, trace_id, span_id, level, message) enable centralized log aggregation in systems like Elasticsearch or Loki. Log levels should be configurable at runtime without redeployment, allowing operators to increase verbosity for specific services during incident investigation.

Health checks must distinguish between liveness and readiness probes. Liveness checks verify the process is running and not deadlocked, while readiness checks confirm the service can handle traffic (database connections established, caches warmed, dependent services reachable). Kubernetes uses these probes to manage pod lifecycle — a failing liveness check triggers a restart, while a failing readiness check removes the pod from the service load balancer.

SLI/SLO metrics provide a framework for measuring service reliability. Key SLIs include request latency (p50, p95, p99), error rate, and throughput. SLOs define target values for these indicators (e.g., 99.9% of requests complete within 500ms). Error budgets — the allowed amount of unreliability — guide engineering priorities: when the error budget is nearly exhausted, teams shift focus from features to reliability work.
