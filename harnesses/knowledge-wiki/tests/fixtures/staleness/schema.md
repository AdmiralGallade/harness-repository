---
domain: Test wiki for staleness detection validation
description: >
  Minimal fixture wiki with configured staleness rules for testing
  wiki-stale and wiki-lint check 13 alignment.
---

# Wiki Schema

## Domain Context
Test fixture for staleness engine validation. Contains articles with varied
updated dates and tags to exercise threshold logic.

## Custom Tags
- fast-moving
- stable-domain
- general

## Hierarchy Roots
- test-concepts

## Staleness Rules

```yaml
staleness_rules:
  default_days: 90
  overrides:
    - tags: [fast-moving]
      days: 30
    - tags: [stable-domain]
      days: 365
```

## Conventions
- Test fixture only — not a real wiki.
