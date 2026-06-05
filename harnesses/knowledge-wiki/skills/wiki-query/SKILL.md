---
name: wiki-query
description: "Use when the user asks a domain question that the wiki may already answer. Navigates articles and synthesizes an answer. Read-only. Do NOT use for structural wiki changes (use wiki-reorg) or health audits (use wiki-health)."
reads: [<wiki_path>/schema.md, <wiki_path>/index.md, <wiki_path>/articles/**/*.md, $ROOT/.claude/rules/working-knowledge.md]
writes:
  # Tier 1 — unconditional on successful query
  - $ROOT/.claude/rules/working-knowledge.md(uses increment, sort)  # Step 7a
  # Tier 2 — user-gated
  - $ROOT/.claude/rules/working-knowledge.md(append new entries)           # Step 8
  - $ROOT/.claude/rules/active-knowledge.md(promoted entries)              # Step 8a (user-confirmed; uses >= 5 promotion gate)
dispatches: [analyst, writer, reviewer]
tier: complex-orchestration
---

# wiki-query

Answer questions by navigating the project wiki's knowledge base. Strictly read-only -- this skill NEVER creates, modifies, or deletes any wiki file.

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` — the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." Stop.
3. **Articles exist:** Check that `<wiki_path>/articles/` contains at least one `.md` file (in any subdirectory). If empty or only `.gitkeep` files: "Wiki has no articles yet. Run `/wiki-add` followed by `/wiki-absorb` to build content." Stop.

---

## Read-Only for Wiki Files

This skill writes `.claude/rules/working-knowledge.md` (Steps 7a and 8) and `.claude/rules/active-knowledge.md` (Step 8a, user-gated). All other writes are prohibited:

- NEVER modify articles in `<wiki_path>/articles/`
- NEVER modify `<wiki_path>/index.md`, `schema.md`, or `log.md`
- NEVER create new files anywhere in `<wiki_path>/`
- NEVER write to `~/.claude/wikis.json` (no `last_used` touch on read operations)

If the user's question reveals a gap or error in the wiki, report it in the answer. Do not fix it. The user can use `/wiki-add` or other write commands to make corrections.

---

## Section Ownership

This skill OWNS:
- `.claude/rules/working-knowledge.md` — Step 7a (increment/sort, unconditional when file exists)

May UPDATE (user-gated):
- `.claude/rules/working-knowledge.md` — Step 8 (append new entries, evict)
- `.claude/rules/active-knowledge.md` — Step 8a (promotion, user confirms)

Read-only: all files under `<wiki_path>/`.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is **read-only** — in Sub-step 0.6, SKIP the touch step entirely. Do not update `last_used`. Sub-step 0.4 (auto-register an unregistered local wiki) still runs; that one-time setup write is acceptable even for read skills.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever this skill previously used `wiki/`.

### Step 1: Gather context

Read the following and prepare a context summary:
- `<wiki_path>/schema.md` (domain, tags, hierarchy roots, conventions)
- `<wiki_path>/index.md` (article titles, categories, hierarchy tree)
- The user's question (from invocation argument or conversation)

The question may arrive as:
- An explicit `/wiki-query <question>` invocation
- A natural-language question in a project where a wiki has been resolved via Step 0
- A follow-up to a previous wiki-query answer

**Search pre-pass** — use the fallback chain from `~/.claude/skills/knowledge-wiki/search-spec.md`:

1. **Index search (Tier 1/2):** If `<wiki_path>/.wiki-index.db` exists, run:
   ```bash
   uv run --with-requirements ~/.claude/skills/wiki-index/requirements.txt \
     python ~/.claude/skills/wiki-index/search.py query \
     --wiki-path <wiki_path> --query "<question>" --top 10
   ```
   search.py auto-selects hybrid (BM25 + vector) or BM25-only based on available dependencies. If exit code is 0, include the output as a `### Search Results` section in the analyst's Runtime Context. Skip keyword scoring.

2. **Keyword fallback (Tier 3):** If no `.wiki-index.db` exists or search.py exits non-zero, use the following keyword scoring algorithm:

   **Step A — Extract Keywords:** Lowercase the question. Remove stop words (a, an, the, is, are, was, were, of, in, to, for, on, at, by, with, from, as, and, or, but, not, this, that, how, what, which, who, when, where, why, do, does, did, can, could, should, would, will, have, has, had, it, its, i, we, you, they, my, your). Split into words, deduplicate. Keep up to 5 keywords (if more, take the 5 longest).

   **Step B — Grep Frontmatter:** For each keyword, run case-insensitive Grep across `<wiki_path>/articles/` (`glob: "**/*.md"`). Keep only lines starting with `title:`, `aliases:`, or `tags:`. Use parallel Grep calls for all keywords.

   **Step C — Count and Rank:** For each matched article, count distinct keyword matches. Sort descending by count, break ties alphabetically. Take top 10.

   **Step D — Format:** Produce `### Pre-Scored Candidates` block listing articles with matched keywords. If zero matches, omit the section entirely.

If neither search nor keyword scoring returns results, omit both sections entirely — do not include placeholder text.

### Steps 2-6: Orchestration (Analyst -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-query/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-query/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-query/reviewer-prompt.md`
- **Batching:** No
- **User approval gate:** No

**Skill-specific Runtime Context sections** (appended to the standard schema block):

```
### Question
{{the user's question}}

### Index
{{full content of <wiki_path>/index.md}}

### Search Results
{{search.py output from Step 1 Tier 1/2, or omit section if Tier 3 fallback}}

### Pre-Scored Candidates
{{keyword-scored article list from Step 1 Tier 3, or omit section if search was used}}
```

**Skill-specific writer extras:** Append the user's question under `## Question` and the schema summary under `## Schema` alongside the analyst plan. Writer output uses `## Answer`, `## Sources`, and `## Gaps` sections (not the standard files-created format).

**Skill-specific reviewer extras:** Append the user's question under `## Question`, the writer's answer under `## Writer Answer`, and the full content of `<wiki_path>/index.md` under `## Index`.

**Skill-specific revision note:** The revision prompt includes the writer's previous answer and instructs: "Do not fabricate content. Do not drop existing correct citations. Report the revised answer using: ## Answer, ## Sources, ## Gaps."

### Step 7: Completion report

Present the answer to the user in this format:

```
[Answer text synthesized from wiki articles]

Sources: [[article-a|Article A]], [[article-b|Article B]]

[If gaps exist:]
Gaps: The wiki doesn't cover [X]. Run /wiki-add to add this.
```

The answer text comes first, written as clear prose. Sources follow immediately after, listing every article that contributed. If gaps were detected, the Gaps line comes last.

### Step 7a: Increment Working Knowledge Usage Counts

If `$ROOT/.claude/rules/working-knowledge.md` exists (where `$ROOT` is the project root from Step 0):

1. Read the file. Parse each entry's `[uses: N]` prefix and proposition text.
2. For each entry, check if the answer generated in Step 7 semantically references that fact (same concept, not exact string match).
3. For each matched entry, increment `[uses: N]` → `[uses: N+1]`.
4. Re-sort all entries by usage count descending (ties broken by most recent `activated:` date).
5. Write the updated file back.

If the file does not exist, skip entirely. If an entry cannot be parsed (missing `[uses:` prefix or missing `source:` line), skip that entry and warn: `"Skipped malformed entry at line N. Run /dev check W3 to diagnose."`

Read `~/.claude/skills/dev-wiki/working-knowledge-spec.md` for the entry format.

### Step 8: Offer Knowledge Activation

After presenting the answer in Step 7, evaluate whether the answer warrants activation into working knowledge. Read `~/.claude/skills/dev-wiki/working-knowledge-spec.md` for evaluation criteria.

**Check all three criteria:**
1. **Substantive:** answer is >3 sentences long
2. **Multi-source:** answer draws from 2+ wiki articles (check Sources list)
3. **Multi-turn relevance:** the facts would be useful beyond this single question

If ANY criterion fails, do not offer. Skip to Error Handling.

**If all three pass, offer activation:**

```
This answer draws from multiple sources and may be useful in future turns.
Activate key facts into working knowledge? (y/n)
```

**On user confirmation ("y", "yes", "sure"):**

1. Extract 3-5 key propositions from the answer.
2. Evaluate each fact: multi-turn? non-obvious? At least 1 of 2 must pass.
3. Format each passing fact as:
   ```
   - [uses: 1] <distilled proposition>
     source: [[wiki:<slug>]] | activated: <today>
   ```
4. Read existing `.claude/rules/working-knowledge.md` if it exists. When parsing existing entries, skip any that are malformed (missing `[uses:` prefix or `source:` metadata line) and warn: `"Skipped malformed entry at line N. Run /dev check W3 to diagnose."`
5. Append new entries.
6. Sort all entries by usage count descending.
7. If >100 entries, evict lowest-count entries (ties: oldest `activated:` date first) until at 100.
8. Enforce 210-line hard cap. If exceeded after eviction, evict lowest-count entries (ties: oldest `activated:` date first) until within cap.
9. Write the file.

Report: `"Activated N facts into working knowledge (M total entries)."`

**On decline ("n", "no"):** Skip. No file changes.

### Step 8a: Mid-Phase Knowledge Promotion (Optional)

After working-knowledge activation (Step 8) completes — regardless of whether the user activated new facts — check for promotion candidates:

1. Read `.claude/rules/working-knowledge.md`. Scan for entries with `uses` ≥ 5.
2. For each candidate, evaluate the 2-of-3 active-knowledge filter (from `~/.claude/skills/dev-wiki/active-knowledge-spec.md`):
   - **Multi-turn:** Will this fact be needed across multiple turns (not a one-off lookup)?
   - **Non-obvious:** Would the model's parametric knowledge get this wrong?
   - **Phase-dependent:** Does the current active phase depend on this exact fact?
   A fact must pass at least 2 of 3 filters to qualify.
3. Dedup: skip any candidate whose `source:` slug already appears in `.claude/rules/active-knowledge.md`.
4. If qualifying candidates exist, offer:
   ```
   N working-knowledge entries qualify for active-knowledge promotion (compaction-resilient):
   - <proposition> (uses: N, source: slug)
   Promote to active-knowledge? (y/n)
   ```
5. **On confirmation:** Read active-knowledge.md (if absent, create with header and current phase title per `~/.claude/skills/dev-wiki/active-knowledge-spec.md`). Check line count — if adding entries would exceed the 40-line hard cap, report: `"Promotion would exceed 40-line active-knowledge cap. Skipping."` and stop. Otherwise, append under a `### Promoted from working-knowledge` subsection with `from:` and `retrieved:` fields per the active-knowledge-spec format.
6. **On decline or no candidates:** Skip silently.

**Skip conditions:** If `.claude/rules/working-knowledge.md` does not exist, or if no active phase exists (active-knowledge.md has no target), skip entirely.

## Tool Standards

- **Glob** for file discovery (not find/ls via Bash)
- **Grep** for content search (not grep/rg via Bash)
- **Read** for reading files (not cat/head/tail via Bash)
- **Bash** reserved for git, build tools, and system commands with no dedicated tool

## Error Handling

| Error | Response |
|-------|----------|
| Agent tool timeout/error | Surface: "[Phase] failed: [error]. Retry with /wiki-query or investigate." Do not retry automatically. |
| Wiki path not found | "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." STOP. |
| No articles in wiki | "Wiki has no articles yet. Run `/wiki-add` followed by `/wiki-absorb` to build content." STOP. |
| Schema missing/corrupt | "schema.md is missing or corrupted at <wiki_path>/schema.md. The wiki may be corrupted." STOP. |
| Query returns 0 matches | Report gap in answer. Suggest `/wiki-add` to add missing knowledge. |

