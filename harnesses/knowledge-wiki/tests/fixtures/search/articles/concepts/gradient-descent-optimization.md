---
title: Gradient Descent Optimization
aliases: [SGD, Adam optimizer, learning rate]
tags: [machine-learning]
tier: public
status: verified
created: 2026-02-08
---

# Gradient Descent Optimization

Gradient descent is the core optimization algorithm for training neural networks. It iteratively adjusts model parameters in the direction that reduces the loss function.

## Stochastic Gradient Descent

SGD estimates the gradient from a random mini-batch rather than the full dataset. This introduces noise that helps escape local minima and reduces memory requirements. The learning rate controls step size — too large causes divergence, too small causes slow convergence.

## Adam Optimizer

Adam (Adaptive Moment Estimation) maintains per-parameter learning rates using running averages of first and second moments of gradients. It combines the benefits of momentum (faster convergence) and RMSprop (adaptive learning rates). Default hyperparameters (lr=0.001, β1=0.9, β2=0.999) work well for most tasks.

## Learning Rate Scheduling

Reducing the learning rate during training improves convergence. Common schedules: step decay (halve every N epochs), cosine annealing (smooth decrease), warmup (start low, increase, then decrease). Learning rate warmup is essential for training transformers.
