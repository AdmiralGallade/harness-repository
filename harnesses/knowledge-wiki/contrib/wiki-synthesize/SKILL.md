---
name: wiki-synthesize
description: "Use when looking for new insights by connecting existing wiki articles. Generates synthesis articles; creative, not defensive. Do NOT use for answering specific questions (use wiki-query) or on wikis with fewer than 10 articles."
---

# wiki-synthesize

Generate new insight articles by finding connections, gaps, contradictions, and meta-patterns across existing wiki content. This is the wiki's creative engine -- it reads everything, spots what humans miss, and proposes new articles that tie the knowledge base together.

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` — the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." Stop.
3. **At least 5 articles:** Count all `.md` files under `<wiki_path>/articles/` (recursively, excluding `.gitkeep`). If fewer than 5 articles exist: "Wiki has N articles -- need at least 5 for meaningful synthesis. Keep building with `/wiki-add`." Stop. Synthesis needs enough material to find cross-cutting themes.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is a **write operation** — in Sub-step 0.6, update the `last_used` field for the resolved wiki to today's date using the atomic write pattern documented in Sub-step 0.7.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever this skill previously used `wiki/`.

### Step 1: Gather context

Read the following and prepare a context summary:

- `<wiki_path>/schema.md` -- extract domain, description, custom tags, hierarchy roots, conventions
- All articles in `<wiki_path>/articles/` and subdirectories -- build an inventory table and collect summaries:

**Article Inventory:**
| Filename | Category | Parents | Tags |
|----------|----------|---------|------|
| one row per existing article, from frontmatter |

**Article Summaries:**
For each article: filename + first 20 lines of content.

### Steps 2-7: Orchestration (Analyst -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-synthesize/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-synthesize/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-synthesize/reviewer-prompt.md`
- **Batching:** No
- **User approval gate:** Yes (Step 3 in template) -- MANDATORY checkpoint, never skip

**Skill-specific Runtime Context sections** (appended to the standard schema block):

```
### Article Inventory
| Filename | Category | Parents | Tags |
|----------|----------|---------|------|
{{one row per article}}

### Article Summaries
{{for each article: filename + first 20 lines}}
```

**Skill-specific approval gate format:** Present numbered insights with category, title, justification, and source articles. User can "create all", select by number, or "skip". Only proceed with approved insights.

**Skill-specific writer extras:** Append the full content of each source article referenced by approved proposals under `## Source Articles` alongside the approved analyst plan.

### Step 8: Completion report

Report to user:
- What was done (articles created, articles updated with cross-links)
- Any schema proposals to review (point to `<wiki_path>/schema.md` ## Proposed Changes)
- Suggested next steps

Format:

```
Synthesized N insight articles:
- Created: article-name (category), another-article (category)
- Cross-linked: M bidirectional links added across K existing articles
- Schema proposals: P new tags/roots suggested (see schema.md ## Proposed Changes)
```

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user:

"[Phase] failed: [error]. You can retry with /wiki-synthesize or investigate the error."

Do not retry automatically. Do not skip the failed phase.
