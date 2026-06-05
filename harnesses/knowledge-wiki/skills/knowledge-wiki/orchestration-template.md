<!-- Canonical orchestration template -- 2026-04-10 -->
<!-- REFERENCE, DO NOT PASTE. Each wiki skill's SKILL.md should link here rather than copy the pipeline inline. -->
<!-- Skills that use this template: wiki-bootstrap, wiki-add, wiki-absorb, wiki-query, wiki-reorg, wiki-init -->

# Orchestration Template: Analyst -> Writer -> Reviewer Pipeline

This file defines the standard subagent pipeline shared by all wiki skills that dispatch Analyst, Writer, and Reviewer subagents. Each skill references this template and provides skill-specific inputs.

## Pipeline Overview

```
Analyst -> [User Approval Gate (optional)] -> Writer -> Reviewer -> [Revision Loop] -> Completion
```

---

## Dispatch Analyst

1. Read `analyst-prompt.md` from the skill's own directory (e.g., `~/.claude/skills/wiki-bootstrap/analyst-prompt.md`).
2. Append a `## Runtime Context` section containing the context gathered in the skill's context-gathering step. **Context budget:** Include at most 30 article summaries in the inventory. For wikis with >30 articles, include a count + category breakdown instead of full inventory rows. Use this format:

```
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

### [Skill-Specific Context Sections]
{{Each skill appends its own context here -- e.g., Focus Topic, Article Inventory, Inbox Entries, Question, Session Context, Interview Answers, Source Material, etc.}}
```

3. Dispatch via Agent tool:

```
Agent tool:
  description: "<skill-name> -- Analyst phase"
  prompt: [contents of analyst-prompt.md] + [runtime context above]
```

4. Receive the analyst's response. It must contain `## Plan`, `## Classifications`, and `## Risks` sections.

5. **Validate analyst output:** If the response does NOT contain all three required sections (`## Plan`, `## Classifications`, `## Risks`), re-dispatch once with: "Your previous response was missing required sections. You MUST include ## Plan, ## Classifications, and ## Risks." If still malformed after 1 re-dispatch, report to user and stop.

6. **Handle analyst risks:** If the `## Risks` section lists anything other than "None" (ambiguities, coverage gaps, potential overlaps, vague answers needing follow-up), present the risks to the user and ask for guidance. Re-dispatch the analyst with the user's clarifications if needed. Do not re-ask about items that were already clear.

---

## User Approval Gate (skill-dependent)

Some skills require explicit user approval before dispatching the writer. The skill's SKILL.md specifies whether this gate applies and what format to use.

- **Skills with approval gate:** wiki-bootstrap, wiki-reorg
- **Skills without approval gate:** wiki-absorb, wiki-add (ingest modes), wiki-init, wiki-query
- **Skills with conditional gate:** wiki-add (capture-identify mode only)

When the gate applies, present the analyst's plan to the user grouped by hierarchy root or numbered by change. Wait for the user's response before proceeding. If the user rejects, stop gracefully.

---

## Dispatch Writer

0. **Pre-check directories:** Before dispatching, verify that all four category directories exist under `<wiki_path>/articles/`: `concepts/`, `patterns/`, `decisions/`, `action-plans/`. Create any missing with `mkdir -p`. This prevents writer failures on fresh wikis.

1. Read `writer-prompt.md` from the skill's own directory.
2. Append the analyst's full response under `## Analyst Plan`.
3. Append any additional context the skill requires (e.g., article inventory, inbox entries, source content, batch topics).
4. If the skill uses batching and the plan exceeds the batch threshold, split into batches and process sequentially. Report progress between batches.

```
Agent tool:
  description: "<skill-name> -- Writer phase (batch K of N)"
  prompt: [contents of writer-prompt.md] + [analyst plan] + [skill-specific context]
```

5. Receive the writer's response. Expected output sections vary by skill but typically include `## Files Created`, `## Files Modified`, `## Schema Proposals`, and `## Self-Review`.

6. **Verify files exist:** For each file listed in the writer's `## Files Created` section, use the Glob tool to verify it exists on disk. If any declared file is missing, report the discrepancy to the user before dispatching the reviewer.

---

## Dispatch Reviewer

1. Read `reviewer-prompt.md` from the skill's own directory.
2. Append the analyst's plan under `## Analyst Plan`.
3. Append the writer's report (combined across all batches if applicable) under `## Writer Report`.
4. Append any additional context the skill requires (e.g., original source material for wiki-add ingest modes, index content for wiki-query).

```
Agent tool:
  description: "<skill-name> -- Reviewer phase"
  prompt: [contents of reviewer-prompt.md] + [analyst plan] + [writer report] + [skill-specific context]
```

---

## Handle Review Result

Parse the reviewer's response for three fields:

- **Score:** Extract the number from the `Score: N/10` line.
- **Issues:** Extract the bulleted list after `Issues:` (or "none").
- **Verdict:** Extract the value from the `Verdict:` line.

Then branch on the verdict:

- `Verdict: accept` -- proceed to the skill's completion step.
- `Verdict: revise` -- enter revision loop (score 6-8, fixable issues).
- `Verdict: reject` -- escalate to user: "Reviewer rejected with score N/10: [issues]. Please review and decide how to proceed." Do NOT auto-revise on reject.

---

## Revision Loop (max 1 round)

Only entered when `Verdict: revise`. Re-dispatch the writer with a DIFFERENT prompt:

```
Agent tool:
  description: "<skill-name> -- Writer revision"
  prompt: |
    You are fixing issues found by the reviewer in your previous work.

    ## Original Analyst Plan
    [paste analyst's plan]

    ## Reviewer Issues
    [paste reviewer's issues list from the reviewer's response]

    ## Your Job
    Read the files you previously wrote. Fix the issues listed below.
    If your fix requires additional changes to maintain wiki conventions
    (cross-links, frontmatter consistency, index updates), make those too.
    Do not re-read original source material. Do not redo work that was approved.
    Report what you fixed using the standard writer output format.
```

After writer fixes, re-dispatch the reviewer. **Maximum 1 revision round.** If the reviewer's verdict is still `revise` or `reject` after 1 revision, accept the best version and report to the user:

"Reviewer found unresolved issues after 1 revision (score N/10): [issues]. Accepting best version — please review manually."

Do NOT loop more than once. Unbounded loops waste tokens and rarely converge.

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user:

"[Phase] failed: [error]. You can retry with /[skill-command] or investigate the error."

Do not retry automatically. Do not skip the failed phase.
