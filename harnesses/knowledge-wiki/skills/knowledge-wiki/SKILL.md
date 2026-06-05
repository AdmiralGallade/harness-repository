---
name: knowledge-wiki
description: "Route wiki operations and enforce wiki workflow discipline. Use when the user mentions 'wiki', 'knowledge base', or wants to manage project knowledge. Also activated by SessionStart hook when a registered wiki applies to the current directory. Do NOT invoke directly when the user names a specific wiki command — invoke that command instead (wiki-query, wiki-add, etc.)."
---

<EXTREMELY-IMPORTANT>
When a registered wiki applies to the current project (or `./wiki/` exists and can be auto-registered), wiki skills are part of the workflow. Do not wait for the user to explicitly ask -- suggest wiki operations at natural moments.

Captured knowledge that never reaches the wiki is lost knowledge. Enforce the pipeline.
</EXTREMELY-IMPORTANT>

# knowledge-wiki

## The Registry

Wikis are tracked globally in `~/.claude/wikis.json`. Each command resolves its target wiki via the canonical Step 0 template (see `step-0-template.md`). Wiki selection happens in this order:

1. **Explicit:** User passes `--wiki <name>` flag
2. **CWD-scoped:** Exactly one registered wiki has a path matching the current directory
3. **Inference:** Multiple wikis match; dispatch a one-shot inference subagent
4. **Auto-register:** CWD has `./wiki/schema.md` but no registered wiki; register it on first use

If no registered wiki applies and no local `./wiki/` exists, suggest `/wiki-init` to create one.

## The Rule

**When a registered wiki is in scope, wiki operations are always in scope.** You do not need the user to say "wiki" -- if you see an opportunity to capture, query, or maintain the wiki, act on it. Suggest wiki operations at natural moments: after learning something new, after a research phase, after resolving a complex bug, after architectural decisions.

**Automatic triggers:** New knowledge surfaced → `/wiki-add`. External docs to add → `/wiki-add --file` or `/wiki-add --url`. Inbox has 3+ entries → `/wiki-absorb`. Domain question → `/wiki-query`. Wiki thin (0-2 articles) → `/wiki-bootstrap`. No registered wiki and no local `./wiki/schema.md` → `/wiki-init`.

**User-initiated:** `/wiki-health`, `/wiki-reorg`, `/wiki-registry`. See the Command Reference table below for the full routing surface.

## Red Flags

These thoughts mean STOP -- you are rationalizing skipping wiki discipline:

| Thought | Reality |
|---------|---------|
| "I'll capture this later" | You won't. /wiki-add now. |
| "The inbox only has 2 items" | Absorb small batches for quality. |
| "This insight is too small" | Atomic articles are the goal. |
| "I'll reorganize eventually" | Run /wiki-health --audit-only to see if it's needed now. |
| "The wiki already covers this" | Run /wiki-query first. Do NOT skip -- your assumption may be wrong. |

## Workflow Order

```
init (once) -> add (ongoing) -> absorb (periodic) -> health (audit) -> reorg (structural)
episodic entries: consolidate (5+ entries) -> inbox -> absorb -> articles
```

**Never skip absorb.** Raw inbox entries are invisible to query, health, and reorg. Until entries are absorbed into articles, they do not exist as far as the wiki is concerned.

## Skill Classification

### Subagent-driven (Analyst -> Writer -> Reviewer)

These operations dispatch 3 sequential subagents via the Agent tool:

- **/wiki-init** -- Interview, scaffold, review
- **/wiki-add** -- Capture insights or ingest external material, format, review
- **/wiki-bootstrap** -- Research domain, generate foundational articles, review quality
- **/wiki-absorb** -- Analyze inbox, write articles, review quality
- **/wiki-consolidate** -- Scan episodic entries, dedup via search index, extract facts into inbox
- **/wiki-query** -- Search, synthesize answer, verify accuracy
- **/wiki-reorg** -- Analyze structure, restructure, review changes

Max 2 review rounds before escalating to the user. Do not loop indefinitely.

### Single-shot

These run directly without subagent dispatch:

- **/wiki-index** -- Build hybrid search index (FTS5 + sqlite-vec vectors) for a wiki
- **/wiki-registry** -- List or rename registered wikis
- **/wiki-health** -- Dashboard + structural audit + staleness marking (mode-based)

## Command Reference

Route user intent to the correct wiki skill:

| User intent | Route to |
|-------------|----------|
| "Set up a wiki" / "initialize" | /wiki-init |
| "Register existing wiki" / "adopt" | /wiki-init --register <path> |
| "List my wikis" / "show wikis" | /wiki-registry |
| "Rename wiki" / "change wiki name" | /wiki-registry rename <old> <new> |
| "Seed domain knowledge" / "bootstrap" / wiki is empty | /wiki-bootstrap |
| "Add these docs" / "import" | /wiki-add --file or /wiki-add --url |
| "I just learned something" / "capture this" | /wiki-add |
| "Process the inbox" / "absorb" | /wiki-absorb |
| "What does the wiki say about X" | /wiki-query |
| "Build search index" / "index the wiki" | /wiki-index |
| "Check wiki health" / "audit" | /wiki-health --audit-only |
| "Reorganize" / "restructure" | /wiki-reorg |
| "Process episodic entries" / "consolidate" | /wiki-consolidate |
| "Mark stale articles" / "staleness check" | /wiki-health --mark-stale |
| "Wiki stats" / "dashboard" | /wiki-health |

## If Unclear

When the user's wiki intent is ambiguous, ask:

> What would you like to do with the wiki?
>
> - **Registry** -- See all registered wikis or rename one
> - **Bootstrap** -- Seed foundational domain knowledge
> - **Add** -- Save an insight from this session or import external files/docs
> - **Absorb** -- Process inbox entries into articles
> - **Query** -- Ask the wiki a question
> - **Health** -- Dashboard, structural audit, or mark stale articles
> - **Reorg** -- Restructure categories and fix hierarchy

Do not guess. Present the options and let the user choose.
