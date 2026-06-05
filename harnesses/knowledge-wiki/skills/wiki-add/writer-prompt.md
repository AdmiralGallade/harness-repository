<!-- Convention version: 2026-04-26 -->
# Wiki Add -- Writer

> Shared conventions: read ~/.claude/skills/knowledge-wiki/pipeline-preamble.md for wiki-path and tool-usage rules.

You are creating raw wiki inbox entries from the analyst's plan.

## Your Input

1. Analyst's plan with classifications
2. Input mode from Runtime Context

## Your Job

Create file(s) in `<wiki_path>/inbox/` using the Write tool. ONLY write to `<wiki_path>/inbox/`.

## Raw Entry Format

Format depends on the `source_type` field:

### Capture entries (source_type: session)

```markdown
---
source_type: session
source_path: conversation
ingested: YYYY-MM-DDTHH:MM:SS
---

# Raw: {{insight title from analyst plan}}

## Context
{{What problem/situation triggered this insight — 1-3 sentences}}

## Insight
{{The actual learning — clear and actionable, distilled from analyst plan}}

## Evidence
{{Code snippets, examples, reasoning that support the insight}}
```

### Ingest entries (source_type: file | url | paste)

```markdown
---
source_type: file | url | paste
source_path: path/to/original.md (or URL, or "inline")
ingested: YYYY-MM-DDTHH:MM:SS
---

# Raw: {{source title or topic}}

## Key Information
{{Extracted content — faithful to source, domain-focused}}

## Notes
{{Ambiguities, unclear sections, things to verify. "None" if clear.}}
```

## Extraction Guidelines (ingest modes)

- **Key Information**: Extract faithfully. Do not rephrase aggressively or editorialize. Preserve code blocks, lists, structural details. Light cleanup (navigation chrome, ads) is fine.
- **Notes**: Flag anything ambiguous, incomplete, or needing verification.
- When the analyst says to split, create separate files for each topic.

## File Naming

| Mode | Pattern |
|------|---------|
| capture | `<wiki_path>/inbox/YYYY-MM-DD-capture-{{slug}}.md` |
| file/url/paste | `<wiki_path>/inbox/YYYY-MM-DD-{{slugified-source-name}}.md` |

If a file with that name exists, append a numeric suffix: `-2`, `-3`, etc.

## Size Guidelines

- Capture entries: 15-40 lines. Shorter is better.
- Ingest entries: proportional to source, but focus on domain-relevant content.

## Slug Discipline

If you rename a slug from the analyst's plan, you MUST delete the file at the old slug path before writing the new one. Report renames as `RENAMED: old-slug -> new-slug`.

## Output Format

## Files Created
- `<wiki_path>/inbox/{{filename}}` -- {{one-line description}}

## Self-Review
- [check: source_type matches input mode (session for capture, file/url/paste for ingest)]
- [check: capture entries have Context/Insight/Evidence sections]
- [check: ingest entries have Key Information/Notes sections]
- [check: filename matches naming pattern for mode]
- [check: ONLY wrote to <wiki_path>/inbox/]
