---
name: wiki-add
description: "Use when adding content to the wiki inbox — either capturing insights from conversation or ingesting external files, URLs, or pasted material. Do NOT use for processing inbox into articles — use wiki-absorb."
---

# wiki-add

Add content to `<wiki_path>/inbox/` as raw entries for later processing by `/wiki-absorb`. Supports two modes: **capture** (extract insights from the current conversation) and **ingest** (import external material).

---

## Mode Detection

| Invocation | Mode | Behavior |
|------------|------|----------|
| `/wiki-add` (no args) | capture (identify) | Scan conversation for insights |
| `/wiki-add <text>` | capture (explicit) | Capture the stated insight |
| `/wiki-add --file <path>` | file ingest | Read and extract from local file(s) |
| `/wiki-add --url <url>` | URL ingest | Fetch and extract from URL |
| `/wiki-add --paste` | paste ingest | User pastes content inline |

**Aliases (backward-compatible):**
- `/wiki-capture` routes to `/wiki-add`
- `/wiki-capture <text>` routes to `/wiki-add <text>`
- `/wiki-ingest <path>` routes to `/wiki-add --file <path>`
- `/wiki-ingest <url>` routes to `/wiki-add --url <url>`

---

## Pre-checks

Step 0 below runs FIRST and resolves `wiki_path`. These pre-checks run after Step 0.

1. **wiki exists:** Verify `<wiki_path>` is a directory. If not found: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry` to see registered wikis." Stop.
2. **schema.md readable:** Read `<wiki_path>/schema.md`. If missing or unparseable: "schema.md is missing or corrupted at <wiki_path>/schema.md." Stop.
3. **inbox/ exists:** If `<wiki_path>/inbox/` does not exist, create it silently and continue.

---

## Orchestration Flow

### Step 0: Resolve Wiki

Read and follow the canonical template at `~/.claude/skills/knowledge-wiki/step-0-template.md`.

This skill is a **write operation** — in Sub-step 0.6, update the `last_used` field for the resolved wiki.

After Step 0 completes, `wiki_path` is the canonical absolute path to the resolved wiki.

### Step 1: Gather Context (Mode-Dependent)

Read `<wiki_path>/schema.md` (domain, tags, hierarchy roots, conventions).

**Capture mode (no --file/--url/--paste):**
- Determine sub-mode: explicit (user provided text) or identify (no text).
- If identify mode: scan recent conversation for problems solved, decisions made, patterns discovered.

**Ingest mode (--file, --url, or --paste):**
- `--file <path>`: Expand globs, read each file. If a source exceeds 200 lines, include first 200 and note truncation.
  - **Binary format pre-processing:** Before the analyst receives file content, check the file extension against supported conversion formats (.pdf, .docx, .pptx, .xlsx, .html, .htm, .png, .jpg, .tiff, .epub). If conversion is needed:
    1. Run via Bash: `uv run --with-requirements ~/.claude/skills/wiki-index/requirements-convert.txt python ~/.claude/skills/wiki-index/convert.py --file <path>`. If `schema.md` specifies `conversion.preferred_engine`, pass `--engine <engine>`. Output goes to stdout by default.
    2. Capture the markdown output and pass it to the analyst as the source material.
    3. If conversion fails, report the error with install suggestions: "Conversion failed. Try: `pip install kreuzberg>=4.9` (or `pip install docling` for better table support)."
    4. For .md, .txt, and .rst files: read directly without conversion (current behavior).
  - See `~/.claude/skills/knowledge-wiki/conversion-spec.md` for the tiered engine architecture and format matrix.
- `--url <url>`: Fetch content using WebFetch and extract meaningful text.
- `--paste`: Prompt user for inline content if not already provided.
- Multiple sources in a single invocation are fine — process each separately.

### Steps 2-4: Orchestration (Analyst -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard A->W->R pipeline. This skill follows that template with:

- **Analyst prompt:** `~/.claude/skills/wiki-add/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-add/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-add/reviewer-prompt.md`
- **Batching:** No
- **User approval gate:** Capture identify mode only (present insight, ask "Want me to capture it?")

**Skill-specific Runtime Context sections** (appended to the standard schema block):

```
### Input Mode
{{capture-explicit | capture-identify | file | url | paste}}

### Source Material (ingest modes)
{{for each source: filename/URL, content}}

### Session Context (capture modes)
{{recent conversation context — problems solved, decisions made, patterns discovered}}

### Explicit Insight (capture-explicit only)
{{the user's argument text}}
```

**Skill-specific writer extras (ingest modes):** Append source material content under `## Source Content` alongside the analyst plan.

**Skill-specific reviewer extras (ingest modes):** Append original source material under `## Original Source` for extraction completeness verification.

### Step 5: Completion Report

Report to user:
- What was added (title and filename for each inbox entry created)
- Source attribution (conversation, file path, or URL)
- Count of items currently in `<wiki_path>/inbox/`
- If inbox has 3+ items: "Your inbox has N items — consider running `/wiki-absorb` to process them into articles."

---

## Scope Boundaries

This command writes ONLY to `<wiki_path>/inbox/`. It does not touch:
- `<wiki_path>/index.md`
- `<wiki_path>/log.md`
- `<wiki_path>/articles/`
- `<wiki_path>/schema.md`

---

## Tier and Lifecycle

Inbox entries carry a tier hint based on input mode. See `tier-spec.md` for canonical definitions.

| Input Mode | Default Tier | Rationale |
|-----------|-------------|-----------|
| capture (any) | `private` | Session insights are personal analysis |
| file | `public` | External reference material is typically factual |
| url | `public` | Published web content is citable |
| paste | `private` | Pasted notes may be personal analysis |

The user may override with `--tier public` or `--tier private`. Final tier assignment happens during absorb.

Status is not set at add time — it is assigned during absorb (see `lifecycle-spec.md`).

---

## Error Handling

If any Agent tool call fails (timeout, error), surface the error to the user:

"[Phase] failed: [error]. You can retry with /wiki-add or investigate the error."

Do not retry automatically. Do not skip the failed phase.
