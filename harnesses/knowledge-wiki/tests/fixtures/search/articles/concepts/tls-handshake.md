---
title: TLS Handshake
aliases: [TLS, SSL, HTTPS handshake]
tags: [security, networking]
tier: public
status: verified
created: 2026-01-25
---

# TLS Handshake

TLS (Transport Layer Security) encrypts communication between clients and servers. The handshake establishes a shared secret key and verifies the server's identity through certificates.

## TLS 1.3 Handshake

TLS 1.3 reduces the handshake to one round trip. The client sends supported cipher suites and a key share. The server responds with its certificate, chosen cipher, and key share. Both derive the session key from the Diffie-Hellman exchange.

## Certificate Verification

The client verifies the server's certificate against trusted certificate authorities (CAs). It checks the certificate chain, expiration date, and that the subject matches the requested domain. Certificate Transparency logs provide public auditability.

## Performance Impact

TLS adds latency from the handshake and CPU overhead from encryption. Session resumption (TLS 1.3 0-RTT) and hardware AES acceleration mitigate this. Modern servers handle millions of TLS connections with negligible overhead.
