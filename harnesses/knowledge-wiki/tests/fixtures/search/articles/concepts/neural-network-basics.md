---
title: Neural Network Basics
aliases: [neural networks, deep learning basics]
tags: [machine-learning]
tier: public
status: verified
created: 2026-02-05
---

# Neural Network Basics

Neural networks are computational models inspired by biological neurons. They consist of layers of interconnected nodes that transform input data through weighted connections and activation functions.

## Architecture

A neural network has an input layer, one or more hidden layers, and an output layer. Each connection has a weight that is learned during training. The network applies a non-linear activation function (ReLU, sigmoid, tanh) at each node to enable learning complex patterns.

## Training with Backpropagation

Training minimizes a loss function by adjusting weights. Backpropagation computes the gradient of the loss with respect to each weight using the chain rule. Optimizers like Adam and SGD use these gradients to update weights iteratively.

## Common Architectures

Convolutional networks (CNNs) excel at image tasks. Recurrent networks (RNNs, LSTMs) handle sequential data. Transformers use self-attention and dominate NLP tasks. Each architecture encodes different inductive biases about the data structure.
