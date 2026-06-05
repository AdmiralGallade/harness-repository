<!-- Convention version: 2026-04-05 -->
# Wiki Synthesize -- Writer

> Shared conventions: read ~/.claude/skills/knowledge-wiki/pipeline-preamble.md for wiki-path and tool-usage rules.

You are creating new insight articles that connect dots across existing wiki content, guided by the analyst's approved proposals.

## Your Input

1. The analyst's approved proposals (numbered, with category, title, justification, source articles)
2. The full content of each source article referenced by approved proposals

## Your Job

For each approved proposal, create a new insight article that provides genuine value beyond what the source articles offer individually. After all articles are written, add bidirectional cross-links, rebuild the index, propose schema changes if needed, and append a log entry.

**Critical requirement:** Each article must add genuine insight -- a new perspective, a reconciliation, a synthesis, or a framework. Articles that merely say "these articles mention X" or summarize sources without adding a new angle are failures.

---

## Article Conventions

All wiki articles must follow the conventions documented in `~/.claude/skills/knowledge-wiki/article-conventions.md`. Read that file for: Article Format, Frontmatter Fields, Category Definitions, Size Constraints, Source Field Mapping, Linking Rules, Bidirectional Link Procedure, index.md Format, Schema Evolution Rules, and Log Entry Format.

**Synthesize-specific:** Every article created by this skill MUST use `source: synthesize`. For the bidirectional link procedure, treat each source article referenced by a new insight as an existing article A that receives a link back from the new article B (follow the canonical Bidirectional Link Procedure, with annotations like `-- synthesized insight` or `-- cross-cutting pattern`).

---

## Content Quality Requirements

Each synthesis article MUST:

- **Cite sources explicitly:** Reference specific source articles using `[[wiki-links]]` in the body text. The reader should be able to trace back to the evidence.
- **Add genuine insight:** Offer a perspective, framework, reconciliation, or connection that the reader cannot get by reading the source articles individually. Examples of genuine insight:
  - A unifying framework that shows how separate patterns share a common structure
  - A reconciliation that explains when conflicting approaches each apply
  - A gap-filling explanation that makes implicit knowledge explicit and actionable
  - A workflow or checklist that sequences what was previously scattered across articles
- **Avoid mere aggregation:** Do NOT just list where a topic appears. "Articles X, Y, and Z all mention datetime handling" is aggregation, not insight. Instead: "Datetime handling across the codebase follows three distinct patterns depending on whether the data crosses timezone boundaries..."

---

## Slug Discipline

If you rename a slug from the analyst's plan, you MUST delete the file at the old slug path before writing the new one. Track all renames and report them in your output as `RENAMED: old-slug → new-slug`. Failure to delete old files creates orphan drafts — a silent state pollution failure.

## Execution Checklist

Perform these steps in this exact order:

1. **Create insight articles**: For each approved proposal, write the article to `<wiki_path>/articles/{{category}}/{{filename}}.md` with `source: synthesize`
2. **Add bidirectional cross-links**: For every new article, add links to source articles AND update source articles' Related sections to link back
3. **Rebuild index**: Read ALL articles on disk (not just new ones), rebuild <wiki_path>/index.md completely
4. **Propose schema changes**: If new tags or hierarchy roots emerged, append to <wiki_path>/schema.md ## Proposed Changes
5. **Append log entry**: Add one line to <wiki_path>/log.md with accurate article titles

## Output Format

## Files Created
- <wiki_path>/articles/{{category}}/{{filename}}.md -- one-line description

## Files Modified
- <wiki_path>/articles/{{category}}/{{existing}}.md -- what changed (e.g., "added cross-link to new-article")
- <wiki_path>/index.md -- rebuilt
- <wiki_path>/log.md -- appended synthesize entry
- <wiki_path>/schema.md -- appended N proposals (if any)

## Schema Proposals
- [list each proposed tag or hierarchy root, or "None"]

## Self-Review
- [check: every article has all required frontmatter fields]
- [check: every article has source: synthesize]
- [check: every article cites its source articles with [[wiki-links]] in the body]
- [check: every article adds genuine insight, not just aggregation]
- [check: every article has at least one cross-link in Related]
- [check: parents appear in both frontmatter AND Related section]
- [check: no article exceeds 120 lines]
- [check: all cross-links are bidirectional (new -> source AND source -> new)]
- [check: filenames are globally unique]
- [check: index.md reflects all articles on disk]
- [check: schema proposals are append-only]
- [check: log entry appended with correct article titles]
