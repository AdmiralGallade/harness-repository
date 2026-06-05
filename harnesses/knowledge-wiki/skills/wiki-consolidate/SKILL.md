---
name: wiki-consolidate
description: "Use when episodic/ has 5+ unconsolidated entries. Converts raw episodic findings into staged inbox entries via dedup + fact extraction. Do NOT use for capturing new insights (use wiki-add) or for processing inbox entries (use wiki-absorb)."
---

# wiki-consolidate

Process unconsolidated episodic entries through a hybrid Python + A->W->R pipeline. The Python pre-pass (`consolidate.py scan`) handles mechanical dedup via search index cosine similarity. The A->W->R pipeline handles creative fact extraction and inbox entry writing. The Python post-pass (`consolidate.py mark`) updates episodic frontmatter.

Pipeline: `episodic/ -> scan -> manifest -> Analyst -> Writer -> Reviewer -> inbox/ -> mark -> episodic frontmatter updated`

---

## Pre-checks

Step 0 below (in the Orchestration Flow) runs FIRST and resolves `wiki_path` -- the absolute path to the target wiki. These pre-checks run after Step 0 and use that resolved path.

1. **Wiki exists:** Verify `<wiki_path>` is a directory. Step 0 should have caught this, but double-check. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **Episodic directory exists:** Check that `<wiki_path>/episodic/` exists and is a directory. If missing: "No episodic/ directory found at <wiki_path>. Nothing to consolidate." Stop.
3. **Unconsolidated entries present:** Check for `.md` files in `<wiki_path>/episodic/` that are not listed in `<wiki_path>/episodic/.consolidated`. If all entries are already processed: "All episodic entries already consolidated. Nothing to do." Stop.
4. **Search index recommended:** Check that `<wiki_path>/.wiki-index.db` exists. If missing: warn "No search index found. Dedup will be skipped -- all entries classified as candidates. Run `/wiki-index build` first for dedup support." Continue (do not block).
5. **Batch cap:** If more than 10 unconsolidated entries are present, process the first 10 (oldest by filename timestamp). Report the remaining count to the user.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`. It defines all 8 sub-steps (read registry, resolve by --wiki flag / CWD / auto-register / inference, validate, touch).

This skill is a **write operation** -- in Sub-step 0.6, update the `last_used` field for the resolved wiki to today's date using the atomic write pattern documented in Sub-step 0.7.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` as the base.

### Step 1: Run consolidate.py scan

Run via Bash:

```
uv run --with-requirements skills/wiki-index/requirements.txt python skills/wiki-consolidate/consolidate.py scan --wiki-path <wiki_path>
```

Capture the JSON manifest from stdout. The manifest classifies each unconsolidated entry as one of:
- `candidate` -- no close match in existing articles, proceed to fact extraction
- `high_similarity` -- cosine similarity above `consolidation.dedup_cosine_threshold` (default 0.85, configurable per-wiki in registry; see `registry-schema.md`), needs Analyst classification
- `duplicate` -- exact or near-exact match, auto-skipped by scan

Branching:
- If scan reports 0 candidates and 0 high_similarity: "No actionable entries found (all duplicates or already processed)." Stop.
- If scan reports candidates only (no high_similarity): proceed to Step 2 with candidates.
- If scan reports high_similarity entries: the Analyst will need to read the matched articles to classify each as duplicate vs update.

### Steps 2-4: A->W->R Pipeline

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-consolidate/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-consolidate/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-consolidate/reviewer-prompt.md`
- **Batching:** No additional batching (scan already caps at 10)
- **User approval gate:** No

**Skill-specific Runtime Context** (appended to the standard schema block):

```
### Scan Manifest
{{JSON manifest from Step 1}}

### Episodic Entry Contents
{{For each candidate and high_similarity entry: filename, full content}}

### Matched Articles (for high_similarity entries only)
{{For each high_similarity entry: the matched article's full content}}
```

### Step 5: Run consolidate.py mark

For each entry processed by the pipeline, run:

```
uv run --with-requirements skills/wiki-index/requirements.txt python skills/wiki-consolidate/consolidate.py mark --wiki-path <wiki_path> --entry <filename> --result <extracted|duplicate|low-confidence> --facts <N> --inbox-entries <comma-separated-inbox-filenames>
```

This appends consolidation metadata to the episodic entry's frontmatter (see `episodic-conventions.md` for the exact fields: `consolidated_at`, `consolidation_result`, `facts_extracted`, `inbox_entries`).

For entries the Analyst classified as `duplicate`: mark with `--result duplicate --facts 0 --inbox-entries ""`.

### Step 6: Completion Report

```
Consolidated N episodic entries:
- Extracted: X entries -> Y inbox entries
- Duplicate: Z entries (already covered by existing articles)
- Low-confidence: W entries (flagged for manual review)

Inbox entries created: [list]
Remaining unconsolidated: M entries
```

---

## Tier and Lifecycle Assignment

Inbox entries produced by consolidation inherit tier classification from the Analyst's judgment per `tier-spec.md`. Status is set to `draft` (they still need to pass wiki-absorb for full review). Provenance frontmatter includes `source_entries` linking back to the originating episodic entries.

---

## Scope Boundary

NEVER modify episodic entry content body (immutable per `episodic-conventions.md`). Only frontmatter metadata may be appended, and only by `consolidate.py mark`. Inbox entries are written to `<wiki_path>/inbox/`.

---

## Error Handling

If `consolidate.py scan` fails: surface the error and suggest checking the search index. Stop.

If any A->W->R stage fails: surface the error to the user. Do NOT run `consolidate.py mark` for failed entries. Report which entries succeeded and which failed.

"[Phase] failed: [error]. You can retry with /wiki-consolidate or investigate the error."

Do not retry automatically. Do not skip the failed phase.
