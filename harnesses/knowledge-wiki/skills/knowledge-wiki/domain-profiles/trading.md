# Domain Profile: Trading

Financial markets, trading systems, market microstructure, and quantitative strategies. Market data and exchange rules change frequently; statistical methods and theory are more stable.

## key_topics

- market-microstructure
- order-management
- risk-management
- execution-algorithms
- market-data
- regulatory-reporting

## conventions

- Pin observations to specific exchange/venue rules and effective dates.
- Distinguish between live market behavior (volatile) and structural market design (stable).

## staleness_rules

```yaml
staleness_rules:
  default_days: 180
  overrides:
    - tags: [market-data, exchange-rules, pricing]
      days: 60
    - tags: [regulations, reporting-requirements]
      days: 90
    - tags: [theory, statistics, methodology]
      days: 365
```

**Rationale:** Market data feeds and exchange rules change with each trading cycle. Regulatory reporting requirements shift quarterly. Statistical theory and methodology are long-lived.

## consolidation

```yaml
consolidation:
  dedup_cosine_threshold: 0.85
```

**Rationale:** Default threshold. Trading content has moderate semantic diversity — market microstructure topics are distinct enough that the standard 0.85 threshold correctly separates them.
