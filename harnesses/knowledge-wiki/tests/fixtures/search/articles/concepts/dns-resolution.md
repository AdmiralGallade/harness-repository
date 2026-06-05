---
title: DNS Resolution
aliases: [DNS, domain name system, name resolution]
tags: [networking, security]
tier: public
status: verified
created: 2026-01-12
---

# DNS Resolution

DNS translates human-readable domain names into IP addresses. The resolution process involves recursive queries through a hierarchy of nameservers: root, TLD, and authoritative.

## Resolution Process

When a client queries a domain, the recursive resolver checks its cache first. On a miss, it queries root nameservers, which direct to TLD nameservers (.com, .org), which direct to the authoritative nameserver for the specific domain. The result is cached with a TTL.

## DNS Security

DNSSEC adds cryptographic signatures to DNS records, preventing cache poisoning and spoofing attacks. DNS-over-HTTPS (DoH) and DNS-over-TLS (DoT) encrypt DNS queries to prevent eavesdropping on the resolution path.

## Common Record Types

A records map domains to IPv4 addresses. AAAA records map to IPv6. CNAME records create aliases. MX records specify mail servers. TXT records hold arbitrary text, often used for SPF and DKIM email authentication.
