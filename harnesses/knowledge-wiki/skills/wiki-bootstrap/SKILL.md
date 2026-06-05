---
name: wiki-bootstrap
description: "Use when seeding a new wiki OR researching specific topics to enrich a mature wiki via online research. Focus-topic mode works at any wiki size; full-domain-gap-analysis mode is best for sparse wikis. Do NOT use when no wiki exists yet (use wiki-init) or for capturing a single insight (use wiki-add)."
writes:
  # Tier 1 — unconditional writes (every bootstrap run)
  - articles/**/*.md                    # creates new wiki articles
  - index.md                            # full rebuild after each batch
  - log.md(append)                      # append bootstrap entry
  - schema.md(Proposed Changes)         # append-only tag/root proposals
  # Tier 2 — conditional (research phase only)
  - .bootstrap-research/                # temp directory: create before research, delete after writer
---

# wiki-bootstrap

Seed the wiki with foundational domain knowledge by researching the domain, identifying gaps, and batch-generating articles that form a structural backbone. This is the cold-start solution -- after `wiki-init` scaffolds the wiki, bootstrap populates it with established public knowledge so that subsequent captures and ingests have rich context to build on.

---

## Section Ownership

This skill writes to the target wiki (`<wiki_path>/`) only. It does NOT write to `_CURRENT_STATE.md` or any dev-wiki artifact. All writes are scoped to the resolved wiki path from Step 0.

---

## Tier and Lifecycle

Bootstrap articles are always `tier: public` and `status: draft`. Bootstrap produces domain facts from online research — these are public by definition but need human review before promotion to `reviewed` or `verified`. See `tier-spec.md` for tier definitions and `lifecycle-spec.md` for the lifecycle state machine.

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` — the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." Stop.

No minimum article count gate. Bootstrap works at any wiki size (see Usage Modes below).

---

## Usage Modes

Bootstrap supports three usage modes:

- **Full-domain mode** (no focus topic): Performs full domain gap analysis. Best for sparse wikis (<10 articles) where broad coverage is needed. On mature wikis (>=10 articles), the analyst will emit a soft-gate warning recommending focus-topic mode instead.
- **Focus-topic mode** (`/wiki-bootstrap "topic name"`): Researches a specific topic area and seeds articles within that scope. Works at any wiki size -- the primary mode for enriching mature wikis.
- **`--full-domain-scan` escape flag**: Suppresses the soft-gate warning on mature wikis when the user genuinely wants full-domain gap analysis (e.g., after a major domain expansion).

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is a **write operation** — in Sub-step 0.6, update the `last_used` field for the resolved wiki to today's date using the atomic write pattern documented in Sub-step 0.7.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever this skill previously used `wiki/`.

### Step 1: Gather context

Read the following and prepare a context summary:

- `<wiki_path>/schema.md` -- extract domain, description, custom tags, hierarchy roots, conventions
- All existing articles in `<wiki_path>/articles/` and subdirectories -- build an inventory table:

| Filename | Category | Parents | Tags |
|----------|----------|---------|------|
| one row per existing article, from frontmatter |

Note the user's focus topic if one was provided (e.g. `/wiki-bootstrap "service meshes"`). If no focus topic was given, record "none" -- the analyst will perform full domain gap analysis.

### Step 2: Dispatch Analyst

Read `analyst-prompt.md` from this skill's directory (`~/.claude/skills/wiki-bootstrap/analyst-prompt.md`). Append the context summary as a `## Runtime Context` section in this format:

    ## Runtime Context

    ### Wiki Path
    {{resolved wiki_path from Step 0}}

    ### Schema
    ---
    domain: {{from <wiki_path>/schema.md}}
    description: {{from <wiki_path>/schema.md}}
    ---

    Domain Context: {{from <wiki_path>/schema.md}}
    Custom Tags: {{bullet list from <wiki_path>/schema.md}}
    Hierarchy Roots: {{bullet list from <wiki_path>/schema.md}}
    Conventions: {{bullet list from <wiki_path>/schema.md}}

    ### Focus Topic
    {{user-provided focus topic, or "none"}}

    ### Article Inventory
    | Filename | Category | Parents | Tags |
    |----------|----------|---------|------|
    {{one row per existing article, from frontmatter}}

Dispatch via Agent tool:

    Agent tool:
      description: "wiki-bootstrap -- Analyst phase"
      prompt: [contents of analyst-prompt.md] + [runtime context above]

Receive the analyst's response.

**Analyst Validation:** Verify the response contains all four required sections: `## Plan`, `## Classifications`, `## Risks`, `## Research Plan`. If any section is missing, re-dispatch the analyst with: "Your response is missing the following required sections: [list]. Please include all four sections." If the second attempt also fails, proceed with available sections and note the gap in the completion report.

**Handle analyst risks:** If the `## Risks` section lists ambiguities, coverage gaps, or potential overlaps that need clarification, present the risks to the user and ask for guidance. Re-dispatch the analyst with the user's clarifications if needed.

**WebSearch fallback:** If the analyst reports that WebSearch calls failed or were unavailable, note affected topics in the completion report as "seeded from training knowledge — verify for accuracy." Do NOT stop the bootstrap. Proceed with available knowledge and flag articles for manual review.

### Step 2.5: Research Phase

Gather web-sourced evidence for the analyst's Research Questions before writing articles. Read `research-loop-spec.md` for the full loop protocol. Summary:

1. **Ceremony-level detection:** Read ceremony level from `.dev-wiki/config.md`. Default to Standard if unknown.
   - Standard: max_rounds=5, max_dispatches=30, coverage_threshold=90%, min_sources=3
   - Lite: max_rounds=1, max_dispatches=5, coverage_threshold=70%, min_sources=1
2. **Note directory:** Create `<wiki_path>/.bootstrap-research/` (clear first if it exists from an interrupted run).
3. **Research loop:** For each round, read `research-agent-prompt.md`, partition questions into topic clusters, dispatch 3-5 parallel research subagents via Agent tool. After each round compute coverage (question covered if distinct sources >= min_sources). Exit when ANY: coverage >= threshold, round == max_rounds, no new sources found, total dispatches >= max_dispatches.
4. **Gap passing:** Uncovered questions pass to the writer (Step 4) flagged: "seeded from training knowledge -- verify for accuracy."
5. **Coverage report:** Print `Research complete: coverage X% (Y/Z questions covered, N rounds, D dispatches)` and list gaps.

### Step 3: Present topic plan for user approval

Present the proposed topics grouped by hierarchy root, not as a flat list:

    Proposed topics (N articles in M groups):

    ## Hierarchy Root A (X articles)
      - Topic Name -- one-sentence description
      - Topic Name -- one-sentence description
      ...

    ## Hierarchy Root B (Y articles)
      - Topic Name -- one-sentence description
      ...

    Remove topics by name, add new ones, or say "looks good."
    Estimated time: ~Z minutes.

The user can:
- **Accept**: proceed with all proposed topics.
- **Remove topics**: drop specific topics by name.
- **Add topics**: include additional topics not in the plan.
- **Reject**: "Bootstrap skipped. You can run `/wiki-bootstrap` later." Stop gracefully.

If the user adds or removes topics, update the plan accordingly before proceeding.

### Step 4: Dispatch Writer (batched)

**Writer pre-checks** (verify before dispatching):
1. Article inventory from Step 1 is non-empty (at least schema.md was read). If empty: "No wiki context gathered. Re-run Step 1." STOP.
2. If Step 2.5 ran (ceremony = Standard or Lite with research enabled), verify `<wiki_path>/.bootstrap-research/` exists and contains at least one note file. If missing: warn "Research notes expected but not found. Writer will rely on training knowledge." Continue.

Read `writer-prompt.md` from this skill's directory (`~/.claude/skills/wiki-bootstrap/writer-prompt.md`).

If the approved plan has more than 10 topics, split into batches of 8-10. Process batches sequentially.

For each batch, append:
- The analyst's full response under `## Analyst Plan`
- The list of topics for this batch under `## Batch Topics`
- The cumulative article inventory (including articles created in previous batches) under `## Article Inventory`

Dispatch via Agent tool:

    Agent tool:
      description: "wiki-bootstrap -- Writer phase (batch K of N)"
      prompt: [contents of writer-prompt.md] + [analyst plan] + [batch topics] + [article inventory]

Receive the writer's response. It must contain `## Files Created`, `## Files Modified`, `## Schema Proposals`, and `## Self-Review` sections.

Report progress between batches: "Batch K of N complete. Created X articles. Starting next batch..."

Update the article inventory with newly created articles before dispatching the next batch.

After all batches complete, dispatch a final cross-link pass:

    Agent tool:
      description: "wiki-bootstrap -- Writer cross-link pass"
      prompt: |
        You are performing a final cross-link pass across all articles created during bootstrap.

        Read all articles in <wiki_path>/articles/ subdirectories. For each article, check if any
        other bootstrap articles reference it. If an article is referenced by others but
        does not link back, add the reverse link to its `related` frontmatter field.

        Also update <wiki_path>/index.md and append to <wiki_path>/log.md.

        Report what you changed using the standard writer output format:
        ## Files Created, ## Files Modified, ## Schema Proposals, ## Self-Review

After all writer batches and the cross-link pass complete, delete `<wiki_path>/.bootstrap-research/` (created in Step 2.5).

### Step 5: Dispatch Reviewer

Read `reviewer-prompt.md` from this skill's directory (`~/.claude/skills/wiki-bootstrap/reviewer-prompt.md`). Append:
- The analyst's plan under `## Analyst Plan`
- The writer's report (combined across all batches and the cross-link pass) under `## Writer Report`

Dispatch via Agent tool:

    Agent tool:
      description: "wiki-bootstrap -- Reviewer phase"
      prompt: [contents of reviewer-prompt.md] + [analyst plan] + [writer report]

### Step 6: Handle review result

Follow the "Handle Review Result" and "Revision Loop" sections from `orchestration-template.md`. If issues found, re-dispatch the writer with reviewer feedback per the revision loop. If approved, proceed to Step 7.

### Step 7: Completion report

Report to user:
- What was done (articles created, cross-links established)
- Any schema proposals to review (point to `<wiki_path>/schema.md` ## Proposed Changes)
- Whether web search was used and for which topics

Format:

    Bootstrapped N articles:
    - Created: article-name (category), another-article (category), ...
    - Cross-linked: X bidirectional links
    - Schema proposals: N new tags/roots for schema review (see schema.md ## Proposed Changes)
    - Web search: used for M topics (topic-a, topic-b, ...) / not used

If multiple batches were processed, include a summary across all batches.

---

## Scope Boundary

NEVER write to `inbox/` or `inbox/.processed/`. NEVER modify `schema.md` directly — propose changes only via `## Proposed Changes` section. All article writes go to `articles/` and its subdirectories only.

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user: "[Phase] failed: [error]. You can retry with /wiki-bootstrap or investigate the error." Do not retry automatically. Do not skip the failed phase.

**Partial batch failure:** If a batch fails after earlier batches succeeded, completed batches survive on disk. The user can re-run `/wiki-bootstrap` to fill gaps -- gap analysis will detect what already exists.
**User rejects all topics:** "Bootstrap skipped. You can run `/wiki-bootstrap` later." Stop gracefully.
**Malformed articles:** If the reviewer flags an article as broken beyond repair, skip it with a warning in the completion report. Process the remaining articles normally.
