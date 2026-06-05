---
title: Data Pipeline Patterns
aliases: [ETL, data pipelines, batch processing]
tags: [databases, machine-learning]
tier: public
status: verified
created: 2026-03-05
---

# Data Pipeline Patterns

Data pipelines move and transform data between systems. They range from simple ETL (Extract, Transform, Load) jobs to complex streaming architectures processing millions of events per second.

## Batch vs Stream Processing

Batch pipelines process data in scheduled intervals (hourly, daily). Stream pipelines process events in near-real-time. Lambda architecture combines both — a batch layer for correctness and a speed layer for low latency. Kappa architecture uses only streaming.

## Idempotent Operations

Pipeline steps should be idempotent — running them multiple times produces the same result. This enables safe retries after failures. Techniques include upserts (INSERT ON CONFLICT), hash-based deduplication, and checkpoint-based exactly-once semantics.

## Monitoring and Observability

Key metrics: throughput (records/second), latency (end-to-end delay), error rate, and backlog size. Data quality checks validate schema, null rates, and value distributions. Alerting on anomalies catches issues before they cascade downstream.
