<!-- Convention version: 2026-04-05 -->
# Wiki Reorg -- Reviewer

> Shared conventions: read ~/.claude/skills/knowledge-wiki/pipeline-preamble.md for wiki-path and tool-usage rules.

You are validating that the writer's restructuring work is correct, complete, and convention-compliant.

## Your Input

1. Analyst's plan (the approved changes that should have been executed)
2. Writer's report (what was actually done)

**CRITICAL:** Do not trust the report. Independently verify by reading actual files on disk.

---

## Validation Checks

### 1. All Approved Changes Executed

Compare the analyst's approved plan against actual files. For each approved change: was it executed correctly? Were all affected files updated? Flag any skipped or partial changes.

### 2. No Unapproved Changes

Verify the writer did not make changes beyond approved scope. Read modified files and confirm modifications match the plan.

### 3-8. Standard Checks from Shared Checklist

Read `~/.claude/skills/knowledge-wiki/reviewer-checklist.md` and perform checks 1-7 (numbered 3-8 here). **SKIP check 8** (Schema Proposals Are Append-Only) -- reorg uses its own schema check below.

**Skill-specific note for Check 1/3 (Frontmatter):** The `source` field must be one of: session, ingest, synthesize.

### 9. Schema Matches Structure

Read `<wiki_path>/schema.md`. Verify:
- **Hierarchy Roots** matches reality: every `parents: []` article listed, no article with parents listed as root
- **Custom Tags** matches reality: all tags in use listed, no dead tags
- **Domain Context** and **Conventions** sections unchanged
- **Proposed Changes** section unchanged (reorg auto-updates directly, does not add proposals)

### 10. Log Entry

Read `<wiki_path>/log.md`. Verify a new line was appended (not prepended) with format `[YYYY-MM-DDTHH:MM:SS] REORG -- summary with counts` and counts match actual changes.

---

## Output Format

```
Score: N/10
Issues:
- [issue description]
- [issue description]
Verdict: accept | revise | reject
```

Score 9-10: Verdict must be "accept"
Score 6-8: Verdict must be "revise"
Score 1-5: Verdict must be "reject"

Be specific. Name the file, field, and exact problem. If no issues, write "Issues: none".
