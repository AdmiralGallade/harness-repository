---
name: wiki-absorb
description: "Use when the wiki inbox has 3+ unprocessed entries or before running query/lint/reorg. Converts raw captures into polished cross-linked articles. Do NOT use for capturing new insights (use wiki-add) or when the inbox is empty."
---

# wiki-absorb

Process all raw entries in `<wiki_path>/inbox/` into polished, cross-linked, tagged articles in `<wiki_path>/articles/`. This is Stage 2 of the two-stage pipeline -- the core synthesis engine.

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` — the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." Stop.
3. **Inbox has entries:** Check that `<wiki_path>/inbox/` contains at least one `.md` file that is not `.gitkeep` and is not inside `.processed/`. If the inbox is empty: "Inbox is empty -- nothing to absorb. Use `/wiki-add` to add entries." Stop.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is a **write operation** — in Sub-step 0.6, update the `last_used` field for the resolved wiki to today's date using the atomic write pattern documented in Sub-step 0.7.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever this skill previously used `wiki/`.

### Step 1: Gather context

Read the following and prepare a context summary:

- `<wiki_path>/schema.md` -- extract domain, description, custom tags, hierarchy roots, conventions
- All inbox entries in `<wiki_path>/inbox/` (top-level `.md` files, skip `.gitkeep` and `.processed/`)
- All existing articles in `<wiki_path>/articles/` and subdirectories -- build an inventory table:

| Filename | Category | Parents | Tags |
|----------|----------|---------|------|
| one row per existing article, from frontmatter |

If inbox contains more than 10 entries, batch them into groups of 5-10. Run the full Analyst -> Writer -> Reviewer cycle once per batch. Process batches sequentially and report progress between batches.

### Steps 2-6: Orchestration (Analyst -> Verifier (conditional) -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-absorb/analyst-prompt.md`
- **Verifier prompt:** `~/.claude/skills/wiki-absorb/verifier-prompt.md` (conditional — see Step 3.5)
- **Writer prompt:** `~/.claude/skills/wiki-absorb/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-absorb/reviewer-prompt.md`
- **Batching:** Yes, batch size 5-10 when inbox has >10 entries (run full pipeline cycle per batch)
- **User approval gate:** No

**Skill-specific Runtime Context sections** (appended to the standard schema block):

```
### Inbox Entries
{{for each entry: filename, source_type, first 10 lines}}

### Article Inventory
| Filename | Category | Parents | Tags |
|----------|----------|---------|------|
{{one row per existing article, from frontmatter}}
```

**Skill-specific writer extras:** Append the raw content of each inbox entry under `## Inbox Entries` alongside the analyst plan. If Verification Guidance preambles were generated in Step 3.5, append them alongside the corresponding inbox entries so the writer sees them FIRST.

### Step 3.5: Source-Credibility Verifier (conditional)

After the Analyst returns its plan, check whether any inbox entries require source-credibility verification before writer dispatch.

**Trigger condition:** For each inbox entry in the current batch:
1. The Analyst's output includes a `claim_density: N` field per entry.
2. Read the density threshold from `~/.claude/skills/wiki-absorb/verifier-prompt.md` §Density Threshold (SSOT).
3. If `claim_density >= threshold` for an entry, dispatch the verifier for that entry.

**When triggered (density at or above threshold):**
1. Dispatch a subagent with `~/.claude/skills/wiki-absorb/verifier-prompt.md` as system prompt.
2. Provide the inbox entry's full content as input.
3. The verifier classifies claims as VERIFIED/PARTIAL/AMBER/RED and returns a Verification Guidance preamble.
4. Prepend the Verification Guidance preamble to the inbox entry content before passing to the Writer.
5. The Writer reads the preamble FIRST and MUST apply Amber Corrections and drop/hedge RED-flagged claims.

**fallthrough (density below threshold):**
The entry proceeds through the standard Analyst -> Writer -> Reviewer pipeline unchanged. No verifier is dispatched. This preserves the existing 3-phase contract for low-density entries (session captures, short insights, internal docs).

### Step 7: Move processed entries

After successful processing (all articles written, index rebuilt, log appended):

1. **Dedup check:** Before processing (in Step 1), check `<wiki_path>/inbox/.processed/` for entries with the same filename as current inbox entries. If a match exists, the entry was already absorbed in a prior run — skip it with a note.
2. Create `<wiki_path>/inbox/.processed/` if it does not already exist.
3. Move ALL processed inbox entries into `<wiki_path>/inbox/.processed/` as a single batch. If any individual move fails, report which entries failed but do NOT re-process already-absorbed entries on the next run.

This archives entries rather than deleting them, preserving the audit trail and preventing duplicate articles on partial failure.

### Step 8: Completion report

Report to user:
- What was done (articles created, articles updated)
- Any schema proposals to review (point to `<wiki_path>/schema.md` ## Proposed Changes)
- Suggested next steps

Format:

```
Absorbed N entries:
- Created: article-name (category), another-article (category)
- Updated: existing-article (added 2 cross-links)
- Proposed: N new tags/roots for schema review (see schema.md ## Proposed Changes)
```

If multiple batches were processed, include a summary across all batches.

---

## Tier and Lifecycle Assignment

Every article created or updated by absorb must include `tier` and `status` frontmatter fields. See `tier-spec.md` for canonical tier definitions and `lifecycle-spec.md` for the lifecycle state machine.

- **Tier:** The analyst classifies each entry as `public` (domain facts — verifiable, citable) or `private` (personal analysis — subjective assessments, decisions without external validation). The classification is based on content, not source. If the inbox entry's `source_type` is `session`, default to `private` unless the content is clearly factual. For `file`, `url`, or `paste` sources, default to `public`.
- **Status:** Articles produced by absorb are set to `status: reviewed` (they pass the reviewer subagent as part of the absorb pipeline). Articles flagged with AMBER or RED claims by the verifier are set to `status: draft` instead.
- **Existing articles:** When updating an existing article, preserve its current `tier` and `status` unless the new content changes the classification. If the update adds unverified claims, downgrade `status` to `draft`.

## Scope Boundary

NEVER write to `inbox/` (except moving files to `inbox/.processed/`). NEVER modify `schema.md` directly — propose changes only via `## Proposed Changes` section. All article writes go to `articles/` and its subdirectories only.

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user:

"[Phase] failed: [error]. You can retry with /wiki-absorb or investigate the error."

Do not retry automatically. Do not skip the failed phase.

**Malformed entries:** If the analyst flags an inbox entry as unreadable or lacking frontmatter, skip it with a warning in the completion report. Process the remaining entries normally.
