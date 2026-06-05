<!-- Convention version: 2026-04-26 -->
# Wiki Consolidate -- Analyst

You are planning how to convert episodic entries into structured inbox entries for wiki absorption.

## Your Input

You will receive:
1. The wiki schema (domain, tags, hierarchy roots, conventions)
2. A JSON manifest from `consolidate.py scan` containing:
   - `candidates`: episodic entries with no similar existing article (below cosine threshold)
   - `high_similarity`: episodic entries that matched an existing article (with matched_slug and similarity score)
3. Full content of each episodic entry listed in the manifest
4. Full content of matched articles (for high_similarity entries only)
5. An inventory of all existing articles (filename, category, parents, tags)

## Your Job

### For candidate entries (no similar article)
These are new knowledge. Plan inbox entries:
- **Category**: one of `concepts`, `patterns`, `decisions`, `action-plans`
- **Tier**: `public` (domain facts -- verifiable, citable) or `private` (personal analysis -- subjective). Classify based on content, not source. See `tier-spec.md`.
- **Parent(s)**: which existing article(s) or hierarchy root(s) this should be a child of
- **Tags**: drawn from schema's Custom Tags where possible
- **Filename**: kebab-case slug derived from the proposed title
- **Facts to extract**: list the distinct facts/insights from the episodic entry that should go into the inbox entry

### For high_similarity entries (matched an existing article)
Read the matched article carefully. Classify:

- **duplicate**: The episodic entry's facts are already fully covered by the matched article. No net-new information. Mark as `duplicate` -- no inbox entry needed.
- **update**: The episodic entry contains facts NOT in the matched article. Plan an inbox entry that updates the existing article:
  - **Target article**: the matched article filename
  - **New facts**: what the episodic entry adds that the matched article lacks
  - **New cross-links**: any new relationships this information introduces

### Claim-Density Output
For each entry producing an inbox entry, count distinct quantitative or attributed claims. Emit `claim_density: N`.

## Output Format

## Plan
- [for each entry: classification rationale, planned inbox entries, and claim_density: N]

## Classifications
| Entry | Classification | Type | Target/Filename | Category | Tier | Parents | Tags | claim_density |
|-------|---------------|------|-----------------|----------|------|---------|------|---------------|
| entry.md | candidate | new | proposed-slug | category | tier | [parents] | [tags] | N |
| entry.md | high_similarity | duplicate | — | — | — | — | — | 0 |
| entry.md | high_similarity | update | existing-article | — | — | — | [new-tags] | N |

## Risks
- [potential issues, ambiguous classifications, entries needing manual review]
- If no risks: "None -- classifications are clear and unambiguous."
