# Domain Profile: AML Compliance

Anti-money laundering, sanctions, fraud, and financial crime compliance. Content changes frequently due to regulatory updates, sanctions list revisions, and evolving typologies.

## key_topics

- transaction-monitoring
- sanctions-compliance
- customer-due-diligence
- suspicious-activity-reporting
- regulatory-frameworks
- fraud-typologies
- money-laundering-typologies

## conventions

- Reference specific regulatory citations (PCMLTFA section numbers, BSA provisions, FATF Recommendations).
- Include effective dates for regulatory changes — compliance content is time-sensitive.

## staleness_rules

```yaml
staleness_rules:
  default_days: 180
  overrides:
    - tags: [sanctions, pep-lists, screening]
      days: 30
    - tags: [regulations, directives, legislation]
      days: 90
    - tags: [typologies, methodologies, frameworks]
      days: 365
```

**Rationale:** Sanctions lists change monthly (OFAC, EU, UN). Regulations update quarterly (enforcement actions, guidance). Typologies are stable patterns that evolve slowly.

## consolidation

```yaml
consolidation:
  dedup_cosine_threshold: 0.80
```

**Rationale:** Regulatory language is formulaic — compliance articles on different topics often share boilerplate phrasing, inflating cosine similarity. A lower threshold (0.80 vs 0.85 default) avoids false-positive dedup of genuinely distinct regulatory entries.
