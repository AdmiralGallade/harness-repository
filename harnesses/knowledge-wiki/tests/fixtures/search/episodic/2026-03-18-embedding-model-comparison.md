---
title: Embedding Model Comparison for Local Search
timestamp: 2026-03-18T10:15:00
worker: claude
tier: episodic
status: draft
tags: [machine-learning, databases]
---

Compared embedding models for local wiki search. nomic-embed-text (384 dims, ~137MB ONNX) via fastembed is the best option for CPU-only use. BGE-M3 is higher quality but 8x larger. Sentence-transformers require PyTorch. fastembed uses ONNX Runtime which works cross-platform without GPU dependencies. For wikis under 1000 articles, nomic-embed-text provides sufficient quality with fast inference.
