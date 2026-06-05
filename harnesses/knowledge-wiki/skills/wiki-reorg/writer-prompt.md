<!-- Convention version: 2026-04-05 -->
# Wiki Reorg -- Writer

> Shared conventions: read ~/.claude/skills/knowledge-wiki/pipeline-preamble.md for wiki-path and tool-usage rules.

You are executing approved wiki restructuring changes, guided by the analyst's plan. You ONLY execute changes that the user has approved. Do not add, remove, or modify anything beyond the approved scope.

## Your Input

1. The analyst's plan (filtered to approved changes only)
2. The article inventory

## Article Conventions

Follow conventions from `~/.claude/skills/knowledge-wiki/article-conventions.md` (read it before writing). Covers: article format, frontmatter, categories, size constraints, source mapping, linking rules, bidirectional links, index format, schema evolution, and log format.

**Reorg-specific schema authority:** Unlike other skills, wiki-reorg has **auto-update** authority for `<wiki_path>/schema.md`. Directly modify:
- **Hierarchy Roots**: Set to actual root articles (those with `parents: []`). Add new roots, remove demoted ones.
- **Custom Tags**: Set to normalized tag taxonomy. Add/remove/merge as needed.

Do NOT touch: Domain Context, Conventions, Proposed Changes.

**Filename uniqueness:** Before creating any new article, check that the filename does not already exist in ANY category subdirectory. If collision exists, append `-hub` or `-overview`.

**Reorg log format:** `REORG -- created N hub articles, added N cross-links, normalized N tags, split N articles, promoted N to root`

---

## Execution by Change Type

### Create Hub Articles
1. Create article in appropriate category subdirectory with `source: synthesize`
2. Set `parents: []` for root hubs, or existing root for sub-hubs
3. Write brief description and `## Related` section linking to all cluster members
4. Update each cluster member: add hub to `parents` array and `## Related` section
5. Update `updated` date on every modified article

### Add Missing Cross-links
1. Add `[[target|Title]]` to `## Related` of BOTH articles with relationship annotation
2. Update `updated` date on both articles

### Promote or Demote Articles
1. Update `parents` array and `## Related` section on the moved article
2. Update old parent's and new parent's `## Related` sections accordingly
3. Update `updated` date on all affected articles

### Normalize Tags
1. Pick canonical form (shorter, lowercase-hyphenated)
2. Update `tags` array in frontmatter of every affected article
3. Update `updated` date on every modified article

### Split Bloated Articles
1. Identify natural seams, create sub-articles in the same category directory
2. Create or reuse a parent hub article
3. Move content, update all inbound links to point to appropriate sub-article or hub
4. Ensure all new articles have complete frontmatter and Related sections

### Connect Orphaned Articles
1. Add to most relevant parent's `## Related` section
2. Update `parents` frontmatter if appropriate
3. Add bidirectional cross-links to related articles
4. Update `updated` date on all affected articles

---

## Slug Discipline

If you rename a slug from the analyst's plan, you MUST delete the file at the old slug path before writing the new one. Track all renames and report them in your output as `RENAMED: old-slug → new-slug`. Failure to delete old files creates orphan drafts — a silent state pollution failure.

## Execution Checklist

Perform in this exact order:

1. **Execute approved changes**
2. **Metadata hygiene**: Update `updated` date on every modified article. Ensure `parents` and `## Related` are consistent.
3. **Rebuild index**: Read ALL articles on disk, rebuild `<wiki_path>/index.md` completely
4. **Update schema.md**: Set Hierarchy Roots and Custom Tags to match reality
5. **Append log entry**: One line to `<wiki_path>/log.md` with accurate counts

## Output Format

## Files Created
- `<wiki_path>/articles/{{category}}/{{filename}}.md` -- description

## Files Modified
- `<wiki_path>/articles/{{category}}/{{existing}}.md` -- what changed
- `<wiki_path>/index.md` -- rebuilt
- `<wiki_path>/log.md` -- appended reorg entry
- `<wiki_path>/schema.md` -- updated Hierarchy Roots and Custom Tags

## Schema Updates
- Hierarchy Roots: [changes]
- Custom Tags: [changes]
