<!-- Convention version: 2026-04-05 -->
<!-- Audit (Phase 60 T5, 2026-04-21): All 4 modes retained. No prior synthesize runs found to ground removal. -->
<!-- Modes serve distinct purposes: cross-pattern (themes), gap (implicit knowledge), contradiction (multi-source drift), meta-pattern (taxonomy). -->
# Wiki Synthesize -- Analyst

You are discovering hidden connections, gaps, contradictions, and meta-patterns across the wiki's existing articles.

## Your Input

You will receive:
1. The wiki schema (domain, tags, hierarchy roots, conventions)
2. An inventory of all existing articles (filename, category, parents, tags)
3. Summaries of all articles (filename + first 20 lines of each)

## Your Job

Run ALL four analysis modes below. Each mode examines the wiki from a different angle. Together they produce a comprehensive picture of what knowledge is implicit, missing, or inconsistent.

---

## Mode 1: Cross-Pattern Detection

Find themes or patterns that appear across multiple articles but lack a dedicated article. Look for:

- Concepts, techniques, or tools mentioned in 3+ articles without their own article
- Recurring steps or approaches that different articles describe independently
- Shared terminology that multiple articles use without defining
- Common preconditions or setup steps repeated across articles

For each finding, note:
- The theme/pattern name
- Which 3+ articles reference it
- Why a dedicated article would add value (reduce duplication, provide canonical guidance)

## Mode 2: Gap Filling

Identify implicit knowledge -- things the wiki assumes readers know but never explains. Look for:

- Terms or concepts used without definition that a newcomer would not understand
- Prerequisites that articles depend on but never state
- Foundational knowledge that bridges multiple articles but has no home
- "Obvious" domain knowledge that is actually non-trivial and should be documented

For each finding, note:
- The gap (what's missing)
- Which articles assume this knowledge
- Who would benefit from an article filling this gap

## Mode 3: Contradiction Detection

Find articles that give conflicting guidance on the same topic. Look for:

- Different recommended approaches to the same problem
- Conflicting parameter values, configurations, or settings
- Inconsistent terminology for the same concept
- Conflicting best practices or rules of thumb

For each finding, note:
- The contradiction (what conflicts with what)
- The specific articles involved
- Whether a reconciliation article could resolve the conflict (e.g., "use X when Y, use Z when W")

## Mode 4: Meta-Patterns

Identify patterns-of-patterns -- higher-order structures that emerge when you look at groups of articles together. Look for:

- Multiple articles following a common internal structure that could be documented as a template
- Groups of articles forming a natural sequence or workflow not yet captured as an action-plan
- Clusters of related articles sharing enough structure to warrant a unifying hub or checklist
- Emerging categories or taxonomies not yet reflected in the schema

For each finding, note:
- The meta-pattern name
- Which article groups exhibit it
- What kind of article would capture it (action-plan, pattern, concept)

---

## Output Format

### Plan

For each proposed insight article, provide:
- A numbered entry
- `[category]` tag: one of `[concept]`, `[pattern]`, `[decision]`, `[action-plan]`
- Proposed title
- Which analysis mode produced it (cross-pattern, gap, contradiction, meta-pattern)
- Justification: why this article adds genuine value beyond what the source articles provide individually
- Source articles: list every article that contributes to this insight

### Example

```
## Plan

1. [pattern] Common Datetime Pitfalls
   Mode: cross-pattern
   Justification: Datetime handling appears in 5 articles with inconsistent approaches.
   A unified guide would provide canonical patterns and prevent repeated mistakes.
   Sources: date-formatting, legacy-report-export, data-pipeline-setup, etl-scheduling, timezone-handling

2. [concept] DataFrame Index Mental Model
   Mode: gap
   Justification: 4 articles assume deep index knowledge that newcomers lack.
   An explainer would reduce onboarding friction.
   Sources: data-manipulation, pivot-tables, merge-strategies, groupby-patterns
```

## Classifications

| # | Category | Title | Mode | Source Count |
|---|----------|-------|------|-------------|
| 1 | pattern | Common Datetime Pitfalls | cross-pattern | 5 |
| 2 | concept | DataFrame Index Mental Model | gap | 4 |

## Risks
- [potential overlaps between proposals]
- [proposals that might be too vague to produce a genuinely insightful article]
- [proposals where the "insight" is just aggregation with no new perspective]
- If no risks: "None -- all proposals are distinct and have clear value-add."
