---
title: Zero Trust Architecture
aliases: [zero trust, zero trust network, BeyondCorp]
tags: [security, networking]
tier: public
status: verified
created: 2026-02-28
---

# Zero Trust Architecture

Zero trust is a security model that eliminates implicit trust based on network location. Every request is authenticated and authorized regardless of whether it originates from inside or outside the network perimeter.

## Core Principles

Never trust, always verify. Assume breach. Least privilege access. Every access request is evaluated against identity, device health, location, and behavior patterns. Google's BeyondCorp paper (2014) formalized this approach.

## Implementation Components

Identity provider (authenticate users), device trust evaluation (OS patches, encryption), policy engine (real-time access decisions), micro-segmentation (limit blast radius), and continuous monitoring (detect anomalies post-authentication).

## Network Micro-Segmentation

Instead of a flat network behind a firewall, zero trust creates small segments around individual workloads. Each segment has its own access policy. Lateral movement after a breach is contained to the compromised segment.
