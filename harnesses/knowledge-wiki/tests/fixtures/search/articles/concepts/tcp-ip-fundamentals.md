---
title: TCP/IP Fundamentals
aliases: [TCP, IP, network protocols]
tags: [networking]
tier: public
status: verified
created: 2026-01-10
---

# TCP/IP Fundamentals

TCP/IP is the foundational protocol suite for internet communication. TCP (Transmission Control Protocol) provides reliable, ordered delivery of data. IP (Internet Protocol) handles addressing and routing packets between hosts.

## The Four-Layer Model

The TCP/IP model has four layers: application (HTTP, DNS), transport (TCP, UDP), internet (IP, ICMP), and link (Ethernet, Wi-Fi). Each layer encapsulates the one above it, adding headers for routing and delivery.

## TCP Three-Way Handshake

TCP connections are established with a three-way handshake: SYN, SYN-ACK, ACK. This ensures both sides agree on sequence numbers and are ready to exchange data. Connection teardown uses FIN packets.

## UDP vs TCP

UDP provides connectionless, unreliable delivery — no handshake, no retransmission. It is faster and used for real-time applications like video streaming, DNS lookups, and gaming where low latency matters more than guaranteed delivery.
