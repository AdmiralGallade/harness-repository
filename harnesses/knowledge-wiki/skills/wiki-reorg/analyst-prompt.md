<!-- Convention version: 2026-04-05 -->
# Wiki Reorg -- Analyst

You are analyzing a project wiki's structure and proposing reorganization changes.

## Your Input

1. The wiki schema (domain, tags, hierarchy roots, conventions)
2. An inventory of all articles (filename, category, parents, tags, line count, inbound link count)

## Your Job

Examine the wiki's current structure and identify problems. Propose specific, actionable changes with clear rationale.

---

## Analysis Dimensions

Work through each dimension systematically. Only report genuine problems.

### 1. Orphan Clusters Needing Hub Articles

Find 3+ related articles (shared tags/topics) with no common parent. For each cluster: list articles, explain commonality, propose a hub filename (kebab-case), and where it fits in the hierarchy.

### 2. Missing Cross-links

Find related article pairs (by tags or topic) with no `[[links]]` between them. Name both articles and the relationship.

### 3. Hierarchy Imbalances

Check for roots with too many children (split into sub-hubs) or too few (merge upward). Name the root, child count, and proposed fix.

### 4. Tag Taxonomy Issues

Find: **synonym tags** to merge, **overly broad** tags (used by nearly all articles), **overly narrow** tags (single article, more general tag exists). Name tags and propose action.

### 5. Bloated Articles

Articles exceeding 120 lines. Name the article, line count, natural seams for splitting, and proposed sub-article filenames.

### 6. Orphaned Articles

Articles with zero inbound links. Name the article and propose where it should be linked from.

---

## Output Format

## Plan

For each proposed change:

```
### Change N: [type]
**Action:** [specific action]
**Affects:** [article filenames]
**Rationale:** [why this improves the wiki]
```

Types: `create-hub`, `add-cross-links`, `rebalance-hierarchy`, `normalize-tags`, `split-article`, `connect-orphan`, `promote-to-root`, `demote-from-root`

Number changes sequentially from 1.

## Classifications

| # | Type | Description | Articles Affected |
|---|------|-------------|-------------------|
| 1 | create-hub | Hub for X cluster | article-a, article-b, article-c |

## Risks

- [changes that might surprise the user]
- [ambiguous cases]
- If no risks: "None -- all proposed changes are straightforward."
