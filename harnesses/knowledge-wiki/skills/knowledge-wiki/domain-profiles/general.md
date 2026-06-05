# Domain Profile: General

General-purpose knowledge base with no domain-specific staleness assumptions. Suitable for project documentation, team knowledge, or mixed-domain wikis.

## key_topics

- (none — user defines during wiki-init Q6)

## conventions

- (none beyond the standard article format)

## staleness_rules

```yaml
staleness_rules:
  default_days: 180
```

**Rationale:** The 180-day default is a reasonable middle ground. Users can add tag-specific overrides later via schema.md as domain patterns emerge.

## consolidation

```yaml
consolidation:
  dedup_cosine_threshold: 0.85
```

**Rationale:** Default threshold. No domain-specific adjustment needed for general-purpose wikis.
