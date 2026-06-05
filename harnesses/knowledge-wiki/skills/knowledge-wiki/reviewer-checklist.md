<!-- Canonical reviewer checklist -- 2026-04-10 -->
<!-- REFERENCE, DO NOT PASTE. Each reviewer-prompt.md should link here for the 9 standard checks. -->
<!-- Skills that use this checklist: wiki-bootstrap, wiki-absorb, wiki-reorg, wiki-add (partial -- capture mode only uses format compliance subset) -->

# Standard Reviewer Validation Checks

These 9 checks are common across all wiki reviewer prompts. Perform ALL of them unless the skill's reviewer-prompt.md explicitly says to skip specific checks.

**IMPORTANT -- Wiki Path:** The Runtime Context will include a `### Wiki Path` field containing the absolute path to the target wiki directory. All file paths below use `<wiki_path>` as a placeholder. Replace it with the actual path from Runtime Context when reading or writing files.

## CRITICAL: Do Not Trust the Report

The writer's report may contain errors or omissions. You MUST independently verify by reading the actual files on disk. Do not assume the report is accurate.

---

## Check 1: Frontmatter Completeness

Read each article file listed in the writer's report. Verify ALL required fields are present and valid:

| Field | Required | Valid Values |
|-------|----------|--------------|
| title | yes | Non-empty string |
| aliases | yes | Array (can be empty []) |
| category | yes | One of: concepts, patterns, decisions, action-plans |
| tags | yes | Array of lowercase hyphenated strings |
| parents | yes | Array of filenames (can be empty [] for roots) |
| created | yes | ISO date (YYYY-MM-DD) |
| updated | yes | ISO date (YYYY-MM-DD) |
| source | yes | One of: session, ingest, synthesize, bootstrap, consolidated (skill-specific -- see reviewer-prompt.md for which value(s) are valid) |
| tier | yes | `public` or `private` (validated in detail by Check 11) |
| status | yes | `draft`, `reviewed`, `verified`, `stale`, or `archived` (validated in detail by Check 12) |

Flag any missing field, empty required field, or invalid value.

## Check 2: Cross-links in Related Section

Every article MUST have at least one `[[cross-link]]` in its Related section. Check:
- The `## Related` section exists
- It contains at least one `[[filename|Display Text]]` link
- Links use the correct format (no path prefixes -- `[[my-article]]` not `[[patterns/my-article]]`)

## Check 3: Parents in Both Places

For every article with non-empty `parents` in frontmatter:
- Each parent filename in `parents: [...]` MUST also appear as a `[[parent-filename|...]]` link in the Related section
- Each parent link in Related MUST be annotated with `-- parent topic`

## Check 4: Article Size

No article may exceed 120 lines. Count the actual lines of each file. If any article exceeds 120 lines, flag it and recommend splitting.

## Check 5: Bidirectional Links

For every cross-link found:
- If article B links to article A in its Related section, article A MUST link back to article B
- Read both files to verify bidirectionality
- Flag any one-way links

## Check 6: Filename Uniqueness

Collect all article filenames across ALL category subdirectories:
- `<wiki_path>/articles/concepts/`
- `<wiki_path>/articles/patterns/`
- `<wiki_path>/articles/decisions/`
- `<wiki_path>/articles/action-plans/`

No two articles may share the same filename, even in different subdirectories.

## Check 7: Index Reflects All Articles

Read `<wiki_path>/index.md`. Verify:
- Every article on disk appears in the By Category section under its correct category
- Every article on disk appears in the By Hierarchy section (rooted or as a child)
- The Recent section contains the last 10 articles by updated date, newest first
- No phantom entries (articles listed in index but not on disk)

## Check 8: Schema Proposals Are Append-Only

Read `<wiki_path>/schema.md`. Verify:
- The `## Custom Tags` section is unchanged from before the operation
- The `## Hierarchy Roots` section is unchanged from before the operation
- Any new proposals appear ONLY in `## Proposed Changes`
- Proposals follow the format:
  - `- [YYYY-MM-DD] Add tag: {{tag}} (used by N articles)`
  - `- [YYYY-MM-DD] New hierarchy root candidate: {{name}} (N articles, no parent)`

**Exception:** wiki-reorg has explicit authority to update `## Custom Tags` and `## Hierarchy Roots` directly when the user has approved changes. For wiki-reorg, check 8 is replaced by "Schema Matches Structure" (see wiki-reorg reviewer-prompt.md).

## Check 9: Log Entry

Read `<wiki_path>/log.md`. Verify:
- A new line was appended (not prepended, not replacing existing)
- Format: `[YYYY-MM-DDTHH:MM:SS] OPERATION -- summary with counts`
- The OPERATION name matches the skill (BOOTSTRAP, ABSORB, REORG, SYNTHESIZE, etc.)
- Counts match the actual number of created and updated articles

## Check 10: File Count Matches Plan

Count the number of article files the writer created or modified. Compare against the analyst's plan:
- The analyst plan specifies N articles to create/update
- The writer's output should produce exactly N new/updated articles (not more, not less)
- If the count mismatches, flag as HIGH: "Writer produced M files but analyst planned N. Possible slug migration orphans or missing articles."

This check catches the [[writer-subagent-slug-migration-anti-pattern]]: writers that rename analyst-determined slugs mid-pass without deleting the old file, producing orphan drafts.

## Check 11: Tier Validity

Every article must have a `tier` field in its frontmatter with a value of exactly `public` or `private`. See `tier-spec.md` for the canonical tier definitions.

- Missing `tier` field: flag as ERROR
- Invalid value (anything other than `public` or `private`): flag as ERROR

Episodic entries (files in `episodic/`) are NOT articles and are exempt from this check.

Severity: **ERROR**

## Check 12: Status Validity

Every article must have a `status` field in its frontmatter with one of: `draft`, `reviewed`, `verified`, `stale`, `archived`. See `lifecycle-spec.md` for the canonical lifecycle state machine.

- Missing `status` field: flag as ERROR
- Invalid value: flag as ERROR

Severity: **ERROR**

---

## Output Format

```
Score: N/12
Issues:
- [check name]: [specific issue -- what's wrong and how to fix it]
Suggestions:
- Consider: [improvement worth noting but not blocking]
Verdict: accept | revise | reject
```

Score-to-verdict mapping:
- Score 10-12: Verdict must be `accept`
- Score 6-9: Verdict must be `revise`
- Score 1-5: Verdict must be `reject`

If there are no issues, write `Issues: none`.

Be specific. Name the file, the field, and the exact problem. Do not give vague feedback like "some links are missing." Say which article is missing which link.
