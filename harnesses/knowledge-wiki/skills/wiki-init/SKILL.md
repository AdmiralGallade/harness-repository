---
name: wiki-init
description: "Use when starting a wiki for a project that does not have one. Interviews the user and scaffolds the wiki directory with schema.md. Do NOT use if a wiki already exists in the project — use wiki-bootstrap to seed content into an existing wiki."
---

# wiki-init

Initialize a project-specific wiki through a short interactive interview, then scaffold the full `wiki/` directory structure with all required files via subagent pipeline.

---

## Invocation Modes

wiki-init has two modes:

- **Create mode:** `/wiki-init` (no arguments) -- interactive interview, scaffolds a new wiki, appends to registry.
- **Register mode:** `/wiki-init --register <path>` -- registers an existing wiki (with schema.md) to the registry. No scaffolding, no interview beyond name/description prompts.

Detect which mode to use based on the user's invocation and branch accordingly. The remainder of this orchestration flow describes Create mode. Register mode is described in the "Register Mode" section at the end of this file.

---

## Pre-checks

Before starting the interview, verify:

1. **wiki/ already exists?** If yes: warn the user that a wiki is already initialized. Show the existing `wiki/schema.md` domain line if present. Ask the user to explicitly confirm they want to re-initialize. If they do not confirm, stop gracefully. Never silently overwrite an existing wiki.

---

## Orchestration Flow

### Step 1: Interactive Interview (in main conversation)

Ask ONE question at a time. Wait for the user's answer before proceeding to the next question. Offer a sensible default in parentheses so the user can just press enter or say "that works" to accept it.

Keep the tone conversational, not interrogative -- this should feel like a quick onboarding chat, not a bureaucratic form.

**Q1: Wiki Name**
> What should we call this wiki? This is the name you'll use with `/wiki-registry` and `--wiki <name>`.
> *(default: derived from the target directory name, e.g., "knowledge-wiki" for /Users/x/knowledge-wiki/)*

The name must be kebab-case (lowercase letters, digits, hyphens). If the user provides invalid characters, normalize or ask again. Reject leading/trailing hyphens and consecutive hyphens.

Verify the name is not already in the registry at `~/.claude/wikis.json` (if the file exists). If it is: "A wiki named '[name]' is already registered. Choose a different name." Re-ask until unique.

**Q2: Wiki Path**
> Where should this wiki live on disk?
> *(default: ./wiki relative to the current directory)*

Accept any absolute or relative path. Resolve to canonical absolute path (use Bash `realpath` on the parent directory, since the target may not exist yet; then append the basename).

Verify the resolved path is not already registered. If it is: "A wiki is already registered at this path: [existing-name]. Choose a different path or use /wiki-registry rename to change its name." Re-ask or abort.

Verify the path does not already contain a `schema.md` (that would indicate an existing wiki that should use `/wiki-init --register` instead). If it does: "A wiki already exists at [path]. Use `/wiki-init --register [path]` to register it instead of creating a new one." Abort.

**Q2.5: Domain Profile (optional)**
> Would you like to start from a domain profile? Profiles pre-fill key topics, conventions, and staleness thresholds with sensible defaults for common domains. You can customize everything afterward.
>
> Available profiles (from `~/.claude/skills/knowledge-wiki/domain-profiles/`):
> - **aml-compliance** — Anti-money laundering, sanctions, financial crime. Aggressive staleness (30d sanctions, 90d regulations).
> - **trading** — Financial markets, execution, risk. Moderate staleness (60d market data, 90d regulations).
> - **machine-learning** — ML engineering, MLOps, model development. Moderate staleness (90d frameworks, 60d APIs).
> - **general** — No domain-specific defaults. Conservative 180-day staleness.
> - **skip** — No profile, configure everything manually.
>
> *(default: skip)*

If the user selects a profile, read the corresponding file from `~/.claude/skills/knowledge-wiki/domain-profiles/<profile>.md` and extract its `key_topics`, `conventions`, and `staleness_rules` sections. These will pre-fill later questions:

- **Q6 (Key Topics):** Pre-fill defaults from the profile's `## key_topics` list. Present as: "Based on the [profile] profile, suggested topics: [list]. Adjust or accept?"
- **Q7 (Conventions):** Pre-fill defaults from the profile's `## conventions` list. Present as: "Suggested conventions: [list]. Add more or accept?"
- **Q9 (Staleness Thresholds):** Pre-fill defaults from the profile's `## staleness_rules` block. Present as: "Suggested thresholds: [summary]. Adjust or accept?"

If the user skips profile selection, all subsequent questions use their original defaults (no pre-fill).

**Q3: Domain**
> What domain does this wiki cover?
> *(e.g., "Python microservices architecture", "our company's hiring process", "machine learning ops")*

This becomes the `domain` field in schema.md and anchors all future content decisions.

**Q4: Audience**
> Who is the primary audience for this knowledge?
> *(default: "the development team")*

Understanding audience shapes article tone and depth.

**Q5: Emphasis**
> What should articles emphasize?
> *(e.g., examples, theory, step-by-step instructions, trade-offs, visual diagrams)*
> *(default: "practical examples and trade-offs")*

This guides the writing style for all future articles.

**Q6: Key Topics**
> What key topics do you already know you'll cover?
> *(list a few -- these will seed the initial hierarchy roots)*
> *(default: derive 2-3 from the domain answer)*

These become the initial hierarchy roots in schema.md.

**Q7: Conventions**
> Any domain-specific conventions articles should follow?
> *(e.g., "always include a code example", "reference RFC numbers", "link to Jira tickets")*
> *(default: "none beyond the standard article format")*

**Q8: Source Materials (optional)**
> Any source materials ready to ingest now? File paths, URLs, or directories you'd like to feed in?
> *(optional -- you can skip this and ingest later)*

If the user provides paths, do NOT ingest them during init. Record them for a reminder to run `/wiki-add --file` after initialization.

**Q9: Staleness Thresholds (optional)**
> How quickly does knowledge in this domain go stale? You can set a default threshold and per-tag overrides.
> *(default: 180 days. Fast-moving domains like sanctions/regulations may need 30-90 days. Stable domains like methodologies may use 365 days.)*

If the user provides thresholds, record them as `staleness_rules` in schema.md. If skipped, use the default (180 days, no overrides). This enables lifecycle-spec.md staleness detection (wiki-health check 13). See `tier-spec.md` and `lifecycle-spec.md` for the tier and lifecycle models that staleness feeds into.

Example overrides the user might specify:
- "sanctions lists should be checked monthly" → `{tags: [sanctions], days: 30}`
- "regulations every quarter" → `{tags: [regulations], days: 90}`
- "methodologies are stable for a year" → `{tags: [methodologies], days: 365}`

After collecting all nine answers, proceed to Step 2.

### Steps 2-6: Orchestration (Analyst -> Writer -> Reviewer pipeline)

Read `~/.claude/skills/knowledge-wiki/orchestration-template.md` for the standard Analyst -> Writer -> Reviewer pipeline. This skill follows that template with these skill-specific inputs:

- **Analyst prompt:** `~/.claude/skills/wiki-init/analyst-prompt.md`
- **Writer prompt:** `~/.claude/skills/wiki-init/writer-prompt.md`
- **Reviewer prompt:** `~/.claude/skills/wiki-init/reviewer-prompt.md`
- **Batching:** No
- **User approval gate:** No

**Skill-specific Runtime Context format** (uses interview answers instead of the standard schema block, since no schema exists yet):

```
## Runtime Context

### Wiki Name
{{Q1 answer}}

### Wiki Path
{{resolved absolute path from Q2}}

### Interview Answers
- Q3 (Domain): {{user's answer}}
- Q4 (Audience): {{user's answer}}
- Q5 (Emphasis): {{user's answer}}
- Q6 (Key Topics): {{user's answer}}
- Q7 (Conventions): {{user's answer}}
- Q8 (Source Materials): {{user's answer, or "None provided"}}
```

**Skill-specific writer extras:** Append the interview answers under `## Interview Answers` alongside the analyst plan.

### Step 7: Append to registry (Create mode)

After the writer has successfully scaffolded the wiki and the reviewer has approved (completion of the current Step 6 revision loop handling), append the new wiki to `~/.claude/wikis.json`.

1. Read `~/.claude/wikis.json` into memory. If the file does not exist, treat it as an empty registry: `{"version": 1, "wikis": []}`.
2. Build the new registry entry:

        {
          "name": "<Q1 answer>",
          "path": "<canonical absolute path from Q2>",
          "description": "<derived from Q3 domain + Q4 audience, 1-2 sentences>",
          "registered": "<today's date in YYYY-MM-DD>",
          "last_used": "<today's date in YYYY-MM-DD>"
        }

   If a domain profile was selected in Q2.5 and it includes a `## consolidation` section, add the consolidation config to the entry:

        {
          ...
          "consolidation": {
            "dedup_cosine_threshold": <value from profile>
          }
        }

   If no profile was selected or the profile has no consolidation section, omit the field (consolidate.py falls back to 0.85 default).

3. Append the new entry to the `wikis` array.
4. Use the atomic write pattern:
   - Write the full modified registry to `~/.claude/wikis.json.tmp` using the Write tool
   - Use the Bash tool to run: `mv ~/.claude/wikis.json.tmp ~/.claude/wikis.json`

The registry append happens AFTER the writer/reviewer cycle succeeds. If the scaffolding failed, do not register the wiki.

### Step 8: Completion report

Report: files created, domain/audience/roots from schema, registry confirmation. Suggest `/wiki-bootstrap` for new wikis, `/wiki-add --file <paths>` if source materials provided.

---

## Error Handling

Agent tool failure: surface error, do not retry, do not skip.

---

## Register Mode

Invoked as: `/wiki-init --register <path>`. No subagents, no interview.

**Pre-checks:** Path must exist, `<path>/schema.md` must be readable, path must not already be registered.

**Flow:**
1. Read `<path>/schema.md` — extract `domain` and `description` from frontmatter
2. Ask for registry name (default: directory basename, enforce kebab-case, no collisions)
3. Ask for description (default: from schema.md)
4. Append to `~/.claude/wikis.json` using atomic write (same pattern as Create mode Step 7)
5. Report: name, path, domain, article count (Glob both `articles/` and `wiki/` layouts)

If any step errors, stop. Do not create partial registry entries.
