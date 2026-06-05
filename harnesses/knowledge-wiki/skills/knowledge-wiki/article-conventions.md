<!-- Canonical article conventions — 2026-04-08 -->
<!-- REFERENCE, DO NOT PASTE. Writer prompts in wiki-absorb, wiki-bootstrap, wiki-reorg should link here rather than copy content inline. -->
<!-- Also referenced by wiki-health for its convention-check sections. -->

# Wiki Article Conventions

This file defines the canonical article format, frontmatter, categories, linking rules, and index format for all wiki articles. Every wiki skill that reads or writes articles should follow these conventions.

## Contents

- Article Format (Obsidian-Compatible)
- Required Frontmatter Fields
- Category Definitions
- Size Constraints
- Source Field Mapping
- Linking Rules
- Bidirectional Link Procedure
- index.md Format
- Schema Evolution Rules
- Log Entry Format

## Article Format (Obsidian-Compatible)

Every article lives under `<wiki_path>/articles/{{category}}/` and uses this exact format:

```markdown
---
title: Article Title
aliases: [alternate name, short name]
category: concepts | patterns | decisions | action-plans
tags: [tag-a, tag-b]
parents: [parent-article-filename]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: session | ingest | synthesize
tier: public | private
status: draft | reviewed | verified | stale | archived
---

# Article Title

Brief one-to-two sentence description.

## Content

Main body. Keep focused on a single topic.

## Related

- [[parent-article|Parent Title]] -- parent topic
- [[sibling-article|Sibling Title]] -- related concept
```

## Required Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| title | yes | Human-readable title |
| aliases | yes | Alternative names for Obsidian search (use [] if none) |
| category | yes | One of: concepts, patterns, decisions, action-plans |
| tags | yes | Topic tags, e.g. [caching, performance] |
| parents | yes | Parent article filenames. Use [] for root articles. Can have multiple parents. |
| created | yes | ISO date |
| updated | yes | ISO date of last modification |
| source | yes | session, ingest, synthesize, or bootstrap |
| tier | yes | `public` or `private`. See `tier-spec.md` for semantics and assignment rules. |
| status | yes | `draft`, `reviewed`, `verified`, `stale`, or `archived`. Default: `draft`. See `lifecycle-spec.md` for state machine. |

## Category Definitions

- **concepts** -- What things are. Definitions, explanations, mental models.
- **patterns** -- Reusable approaches. How-tos, recipes, templates.
- **decisions** -- Why choices were made. Trade-offs, rationale, context.
- **action-plans** -- Step-by-step playbooks for common tasks.

## Size Constraints

- Ideal: 40-80 lines
- Hard cap: 120 lines
- If exceeding 120 lines, split into focused sub-articles

## Source Field Mapping

Set the `source` field based on the inbox entry's `source_type` frontmatter:
- `source_type: file` maps to `source: ingest`
- `source_type: url` maps to `source: ingest`
- `source_type: paste` maps to `source: ingest`
- `source_type: session` maps to `source: session`

For synthesized articles, use `source: synthesize`. For articles created by wiki-bootstrap, use `source: bootstrap` (generated from domain knowledge to seed the wiki — distinct from `ingest` which is imported from user-provided files/URLs). For articles created from consolidated episodic entries (via the `/wiki-consolidate` → `/wiki-absorb` pipeline), use `source: consolidated`.

## Linking Rules

- `[[filename]]` for basic cross-references
- `[[filename|Display Text]]` for readable link labels
- NO path prefixes -- `[[my-article]]` not `[[patterns/my-article]]` (Obsidian shortest-match)
- Parents declared in TWO places (both required):
  1. Frontmatter: `parents: [parent-filename]`
  2. Related section: `[[parent-filename|Parent Title]] -- parent topic`
- Tags in frontmatter: `tags: [a, b]` (source of truth)
- Optional inline `#tag` in body for emphasis
- Hub article = any article with 3+ children via parents field
- Cross-links MUST be bidirectional: if B links to A, A must link to B
- Filenames must be globally unique across ALL category subdirectories
- Every article must have at least one cross-link in its Related section. If no related articles exist yet, link to the most relevant hierarchy root.

## Bidirectional Link Procedure

When creating article B that links to existing article A:
1. Add `[[a-article|A Title]]` to B's Related section
2. Read A's current content
3. Add `[[b-article|B Title]]` to A's Related section
4. Report A as a modified file

## index.md Format

Rebuild `<wiki_path>/index.md` completely using this structure:

```markdown
# Wiki Index

## By Category

### Concepts
- [[article-name|Article Title]] -- one-line summary

### Patterns
- [[article-name|Article Title]] -- one-line summary

### Decisions
- [[article-name|Article Title]] -- one-line summary

### Action Plans
- [[article-name|Article Title]] -- one-line summary

## By Hierarchy

- [[root-hub|Root Hub Title]]
  - [[child-article|Child Title]]
    - [[grandchild|Grandchild Title]]

## Recent

- [YYYY-MM-DD] [[article-name|Article Title]] -- one-line summary
```

- By Category: ALL articles grouped by category
- By Hierarchy: tree from parents frontmatter. `parents: []` = root. Indent children. Multi-parent = appears under each.
- Recent: last 10 by `updated` date, newest first
- Write all articles FIRST, then rebuild index in one pass

## Schema Evolution Rules

Skills MUST NOT modify `schema.md`'s `## Custom Tags` or `## Hierarchy Roots` sections directly. Append proposals to `## Proposed Changes` only:

- `- [YYYY-MM-DD] Add tag: {{tag}} (used by N articles)`
- `- [YYYY-MM-DD] New hierarchy root candidate: {{name}} (N articles, no parent)`

Exception: wiki-reorg has explicit authority to update `## Custom Tags` and `## Hierarchy Roots` when the user has approved changes in Step 3 of its orchestration flow.

## Log Entry Format

Append a single line to `<wiki_path>/log.md` for every write operation:

    [YYYY-MM-DDTHH:MM:SS] OPERATION -- summary

Examples:

    [2026-04-05T14:30:00] ABSORB -- 3 articles created, 2 updated, inbox cleared
    [2026-04-05T18:00:00] REORG -- created 6 hub articles for hierarchy roots
    [2026-04-05T19:15:00] BOOTSTRAP -- 12 articles created, batch 1 of 2 processed

Use accurate counts and include the batch number for multi-batch operations.
