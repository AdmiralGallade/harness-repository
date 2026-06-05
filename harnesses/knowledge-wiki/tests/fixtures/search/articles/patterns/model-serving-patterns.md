---
title: Model Serving Patterns
aliases: [ML inference, model deployment, serving infrastructure]
tags: [machine-learning, performance]
tier: public
status: verified
created: 2026-03-01
---

# Model Serving Patterns

Model serving is the infrastructure for running machine learning models in production. It bridges the gap between training (offline, batch) and inference (online, real-time).

## Serving Architectures

Direct embedding: load the model into the application process (fastest latency, simplest). Model server: dedicated inference service (TensorFlow Serving, Triton, vLLM) behind an API. Serverless: function-as-a-service with cold start trade-offs.

## Batching and Optimization

Dynamic batching groups multiple inference requests into a single GPU batch, improving throughput. Model optimization techniques include quantization (FP16, INT8), pruning, and distillation. ONNX Runtime provides cross-platform optimized inference.

## A/B Testing and Canary Deployments

New model versions are gradually rolled out alongside existing ones. Traffic splitting sends a percentage of requests to the new model. Metrics (latency, accuracy, business KPIs) are compared before full rollout. Shadow mode runs both models but only serves results from the current one.
