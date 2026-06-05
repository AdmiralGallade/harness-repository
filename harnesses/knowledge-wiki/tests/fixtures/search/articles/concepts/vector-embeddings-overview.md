---
title: Vector Embeddings Overview
aliases: [embeddings, semantic search, vector search]
tags: [machine-learning, databases]
tier: public
status: verified
created: 2026-02-01
---

# Vector Embeddings Overview

Vector embeddings are dense numerical representations of text, images, or other data. They capture semantic meaning in a high-dimensional space where similar concepts are located near each other.

## How Embeddings Work

An embedding model transforms input text into a fixed-length vector (typically 384-1536 dimensions). The model is trained so that semantically similar texts produce vectors with high cosine similarity. This enables finding related content even when different words are used.

## Embedding Models

Popular embedding models include OpenAI's text-embedding-3, Cohere's embed-v3, and open-source alternatives like nomic-embed-text (via fastembed) and BGE-M3. For local CPU-only use, nomic-embed-text through the fastembed library provides good quality with ONNX runtime acceleration.

## Vector Databases

Specialized databases store and query embeddings efficiently. Options include Pinecone, Weaviate, Qdrant, and local alternatives like sqlite-vec (an extension for SQLite) and LanceDB. For small to medium collections, sqlite-vec provides vector search without requiring a separate database server.
