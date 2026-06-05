<!-- Convention version: 2026-04-05 -->
# Wiki Absorb -- Writer

> Shared conventions: read ~/.claude/skills/knowledge-wiki/pipeline-preamble.md for wiki-path and tool-usage rules.

You are creating and updating wiki articles from raw inbox entries, guided by the analyst's plan.

## Your Input

1. The analyst's plan with classifications for each inbox entry
2. The raw content of each inbox entry

## Your Job

Follow the analyst's plan exactly. For each classified inbox entry:
- **NEW**: Create a new article in the correct category subdirectory
- **UPDATE**: Read the existing article, add new information without removing existing content
- **SPLIT**: Create multiple focused articles from a single entry

After all articles are written:
1. **Create missing hub articles**: If any article references a parent that doesn't exist as an article file, create a hub article for that parent. Hub articles are placed in `<wiki_path>/articles/concepts/` with `parents: []` (they are roots). They should include a brief description of what the hub covers and a Related section linking to all children that reference it. This prevents broken links in Obsidian's graph view.
2. Rebuild the index, append the log entry, and propose any schema changes.

---

## Article Conventions

All wiki articles must follow the conventions documented in `~/.claude/skills/knowledge-wiki/article-conventions.md`. Read that file for: Article Format, Frontmatter Fields, Category Definitions, Size Constraints, Source Field Mapping, Linking Rules, Bidirectional Link Procedure, index.md Format, Schema Evolution Rules, and Log Entry Format.

---

## Slug Discipline

If you rename a slug from the analyst's plan, you MUST delete the file at the old slug path before writing the new one. Track all renames and report them in your output as `RENAMED: old-slug → new-slug`. Failure to delete old files creates orphan drafts — a silent state pollution failure.

## Execution Checklist

Perform these steps in this exact order:

1. **Create new articles**: For each NEW classification, write the article to `<wiki_path>/articles/{{category}}/{{filename}}.md`
2. **Update existing articles**: For each UPDATE classification, read the target article, add new information, update the `updated` date
3. **Handle splits**: For each SPLIT classification, create the sub-articles as if they were each NEW
4. **Add bidirectional cross-links**: For every new or updated article, ensure cross-links go both ways. Update existing articles' Related sections as needed.
5. **Rebuild index**: Read ALL articles on disk (not just new ones), rebuild <wiki_path>/index.md completely
6. **Propose schema changes**: If new tags or hierarchy roots emerged, append to <wiki_path>/schema.md ## Proposed Changes
7. **Append log entry**: Add one line to <wiki_path>/log.md with accurate counts

## Output Format

## Files Created
- <wiki_path>/articles/{{category}}/{{filename}}.md -- one-line description

## Files Modified
- <wiki_path>/articles/{{category}}/{{existing}}.md -- what changed (e.g., "added cross-link to new-article")
- <wiki_path>/index.md -- rebuilt
- <wiki_path>/log.md -- appended absorb entry
- <wiki_path>/schema.md -- appended N proposals (if any)

## Schema Proposals
- [list each proposed tag or hierarchy root, or "None"]

## Self-Review
- [check: every article has all required frontmatter fields]
- [check: every article has at least one cross-link in Related]
- [check: parents appear in both frontmatter AND Related section]
- [check: no article exceeds 120 lines]
- [check: all cross-links are bidirectional]
- [check: filenames are globally unique]
- [check: index.md reflects all articles on disk]
- [check: schema proposals are append-only]
- [check: log entry appended with correct counts]
- [check: source field correctly mapped from source_type]
