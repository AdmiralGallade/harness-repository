# Empirical-Anchor Density (Advisory)

<!-- ADVISORY ONLY - never HARD-block; exit code MUST remain 0 regardless of empirical-anchor findings per [[wiki:two-tier-drift-classification]]. Advisory-fires-but-pass-returned. -->

Advisory dimension orthogonal to the structural checks in SKILL.md. Measures whether concept and pattern articles ground their claims in empirical evidence rather than purely abstract guidance. Informed by the source-credibility-verifier-subagent pattern's density-threshold heuristic.

## 3-count heuristic

For each article with `category: concepts` or `category: patterns`, count the number of empirical anchors present in the article body. An empirical anchor is any of:

1. **Named study or experiment cited** -- a reference to a specific named study, benchmark, experiment, or dated empirical observation (e.g., "Phase 26 J-check validation", "2026-04-17 empirical 54-claim audit")
2. **Quantitative threshold with units** -- a concrete number with context (e.g., "≥3 anchors", "120-line cap", "80% coverage target"), not vague qualifiers ("many", "several")
3. **Primary-source URL or artifact path** -- a direct link to source material, dataset, tool output, or referenced file path that a reader can verify

Target: **≥3** empirical anchors per concept/pattern article. Articles below this threshold receive an advisory note.

## Exemptions

Do NOT apply this dimension to:

- **Meta-pattern hub articles** -- these aggregate and link to member articles that carry their own anchors
- **Decision articles** (`category: decisions`) -- these document choices, not empirical claims
- **Action-plan articles** (`category: action-plans`) -- these prescribe steps, not empirical claims
- **Pre-bootstrap wikis** -- wikis with fewer than 10 articles are still in bootstrap phase and lack sufficient content for meaningful anchor density assessment

## Advisory output format

When an article falls below the ≥3 threshold, append a line to the INFO section of the report:

```
INFO:
- Empirical-anchor density: article X has 1 anchor; 3+ recommended. Consider backfilling from [source-URL-list].
```

This dimension MUST NOT elevate to WARNING or ERROR. It is strictly informational. The overall lint exit code is unaffected by empirical-anchor findings.
