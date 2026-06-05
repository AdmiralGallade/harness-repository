---
title: Transformer Architecture
aliases: [transformers, self-attention, attention mechanism]
tags: [machine-learning]
tier: public
status: verified
created: 2026-02-10
---

# Transformer Architecture

The transformer architecture, introduced in "Attention Is All You Need" (2017), uses self-attention mechanisms to process sequences in parallel without recurrence. It is the foundation of modern language models like GPT, BERT, and Claude.

## Self-Attention

Self-attention computes a weighted sum of all input positions for each output position. The weights are determined by query-key dot products, allowing the model to focus on relevant parts of the input regardless of distance. Multi-head attention runs multiple attention computations in parallel.

## Positional Encoding

Since transformers have no inherent notion of sequence order, positional encodings are added to input embeddings. Original transformers used sinusoidal encodings. Modern variants use rotary position embeddings (RoPE) which encode relative positions through rotation matrices.

## Scaling Laws

Transformer performance scales predictably with model size, data size, and compute. Kaplan et al. (2020) showed power-law relationships between these factors and loss. This enables predicting performance of larger models before training them.
