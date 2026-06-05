---
name: wiki-reorg
description: "Use when the wiki has structural problems (missing hubs, weak hierarchy, stale organization) and needs gardening. Restructures categories and links. Do NOT use for read-only diagnosis — run wiki-health --audit-only first to identify issues before reorganizing."
---

# wiki-reorg

Restructure the project wiki's hierarchy, create hub articles for orphan clusters, add missing cross-links, normalize tags, and split bloated articles. This is the gardening operation -- it takes a wiki that has grown organically and gives it deliberate structure.

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` — the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." Stop.
3. **Articles exist:** Check that `<wiki_path>/articles/` contains at least one `.md` file in any subdirectory. If empty: "Wiki has no articles yet. Run `/wiki-add --file` to add content, then `/wiki-absorb` to process it." Stop.
4. **Recommend audit first:** Suggest running `/wiki-health --audit-only` first to see current issues. The audit report identifies orphans, bloat, broken links, and tag drift -- useful context for a reorg. If the user has already run an audit recently, proceed.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is a **write operation** — in Sub-step 0.6, update the `last_used` field for the resolved wiki to today's date using the atomic write pattern documented in Sub-step 0.7.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever this skill previously used `wiki/`.

### Step 1: Gather context

Read the following and prepare a context summary:

- `<wiki_path>/schema.md` -- extract domain, description, custom tags, hierarchy roots, conventions
- All articles in `<wiki_path>/articles/` and subdirectories -- build an inventory table with line counts and inbound link counts:

| Filename | Category | Parents | Tags | Lines | Inbound Links |
|----------|----------|---------|------|-------|---------------|
| one row per article, from frontmatter + file stats |

To compute Inbound Links: for each article, count how many OTHER articles contain a `[[filename]]` or `[[filename|...]]` reference to it.

### Steps 2-7: Orchestration (Analyst -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-reorg/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-reorg/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-reorg/reviewer-prompt.md`
- **Batching:** No
- **User approval gate:** Yes (Step 3 in template) -- this is the critical gate

**Skill-specific Runtime Context sections** (appended to the standard schema block):

```
### Article Inventory
| Filename | Category | Parents | Tags | Lines | Inbound Links |
|----------|----------|---------|------|-------|---------------|
{{one row per article, including line count and inbound link count}}
```

**Skill-specific approval gate format:** Present numbered changes with rationale. User can "proceed with all", select by number (e.g., "1, 3, 5"), or "cancel". After user selection, create a NEW filtered plan containing ONLY approved items. Pass this filtered plan to the writer — the writer MUST NOT see unapproved items.

**Skill-specific writer extras:** Append the full article inventory under `## Article Inventory` alongside the approved analyst plan. Writer output uses `## Files Created`, `## Files Modified`, `## Schema Updates`, and `## Self-Review` sections.

**Cross-link update on rename:** For every renamed article (old-slug → new-slug), the writer MUST grep the entire wiki for `[[old-slug]]` and `[[old-slug|` references and update them to `[[new-slug]]` / `[[new-slug|`. This prevents mass broken links after reorg.

### Step 8: Completion report

Report to user:
- Hub articles created (with filenames and which articles they cluster)
- Cross-links added (which pairs of articles were linked)
- Articles split (original filename, new sub-article filenames)
- Tags normalized (old tag -> new tag, number of articles affected)
- Articles promoted or demoted (filename, old parent -> new parent)
- Schema updates applied (changes to Hierarchy Roots and Custom Tags)
- Index rebuilt (confirm)
- Log entry appended (confirm)

Suggested next steps:
- "Run `/wiki-health` to verify the restructured wiki's health and see the dashboard."

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user:

"[Phase] failed: [error]. You can retry with /wiki-reorg or investigate the error."

Do not retry automatically. Do not skip the failed phase.
