<!-- Canonical Step 0 template — 2026-04-08 -->
<!-- REFERENCE, DO NOT PASTE. Each wiki skill's SKILL.md should link here rather than copy content inline. -->
<!-- To use this template in a skill: write a short Step 0 section that reads "Read and follow ~/.claude/skills/knowledge-wiki/step-0-template.md. This skill is a [write|read-only] operation — in sub-step 0.6 [update the last_used field | SKIP the touch step]." Then link to this file. -->
<!-- Sub-step 0.6 (Touch the registry) is write-only. Read-only skills (wiki-query, wiki-health in read modes) follow the SKIP instruction. -->

### Step 0: Resolve Wiki

**Canonical path definition:** Throughout this template, "canonical path" means the absolute path with symlinks resolved (via `realpath`) and trailing slashes stripped. Use the Bash tool to run `realpath <path>` when comparing paths.

Determine which wiki this command targets. This runs BEFORE any existing pre-checks.

**Sub-step 0.0: Check Session Cache**

Check if `<wiki_path>/.wiki-resolved` exists (where wiki_path is the wiki root discovered in prior invocations). If it exists and was created in this session (check file mtime is within the last 4 hours):

1. Read `.wiki-resolved` for cached discovery results (wiki_path, schema summary, article count).
2. Skip Sub-steps 0.1-0.8 and proceed with the cached values.
3. Emit: "[wiki] Using cached discovery (skip step-0)."

If `.wiki-resolved` does not exist or is stale, proceed with full discovery (Sub-steps 0.1-0.8).

**Sub-step 0.1: Read the registry**

Read `~/.claude/wikis.json`. Handle these cases:
- File does not exist: treat as empty registry `{"version": 1, "wikis": []}`.
- File exists but is unparseable JSON: STOP. Report to user: "Registry at ~/.claude/wikis.json is corrupted. Back up the file and remove it to start fresh, then re-register your wikis with /wiki-init --register <path>."
- File exists and is valid: load it into memory for the rest of Step 0.

**Sub-step 0.2: Explicit --wiki flag**

If the user invoked the command with `--wiki <name>`:
- Look up the wiki by name in the registry.
- If not found: STOP. Report: "No wiki named '<name>' is registered. Run `/wiki-registry` to see available wikis."
- If found: verify the path still exists on disk. If not: STOP. Report: "Wiki '<name>' is registered at '<path>' but the directory does not exist. Restore the directory or use /wiki-registry rename to adjust."
- Verify `<path>/schema.md` exists and is readable. If not: STOP. Report: "Wiki '<name>' at '<path>' is missing schema.md. The wiki may be corrupted."
- If valid: set `wiki_path = <resolved-path>` and skip to Sub-step 0.6.

**Sub-step 0.3: Build the candidate list**

Build the list of candidate wikis:
- A wiki is a candidate if its `path` equals CWD or is a subdirectory of CWD (prefix match on canonical paths).
- A wiki is also a candidate if the user's current message contains the wiki's `name` field as a whole-word match (case-insensitive). The name MUST appear at a word boundary — the character before and after must be a space, punctuation, or string boundary. "ml" must NOT match "html" or "normalizing". For example, "capture this to the aml-compliance wiki" matches `aml-compliance` because hyphens are word boundaries.

**Sub-step 0.4: Auto-register unregistered local wiki**

If CWD contains a `./wiki/` directory with `./wiki/schema.md`, and no registered wiki's path matches the canonical path of `./wiki/`:

1. Derive a name from CWD's PARENT directory basename (not CWD itself), lowercased and kebab-cased (e.g., `/Users/x/my-project/wiki/` → `my-project`). This avoids generic names like "wiki" when CWD is the wiki directory itself.
2. If that name collides with an existing registry entry with a different path, append a numeric suffix: `knowledge-wiki-2`, `knowledge-wiki-3`, etc.
3. Read `./wiki/schema.md`, extract the `description` field from the YAML frontmatter (the line after `description:`, multi-line strings supported).
4. Build the new registry entry:

        {
          "name": "<derived-name>",
          "path": "<canonical absolute path of ./wiki>",
          "description": "<from schema.md, or empty string>",
          "registered": "<today in YYYY-MM-DD>",
          "last_used": "<today in YYYY-MM-DD>"
        }

5. Use the atomic write pattern (see Sub-step 0.7) to append the entry to the registry.
6. Emit a one-line notice: `[Auto-registered '<name>' from ./wiki/. Run /wiki-registry rename to change the name.]`
7. Add the newly registered wiki to the candidate list.

**Sub-step 0.5: Select the wiki**

From the candidate list:
- If zero candidates:
  - If the registry is empty (no wikis registered at all): STOP. Report: "No wikis are registered. Run `/wiki-init` to create your first wiki, or `/wiki-init --register <path>` to adopt an existing one."
  - If the registry has wikis but none match CWD: STOP. Report: "No wiki applicable to this directory. Use --wiki <name> or cd into a project with a registered wiki. Run /wiki-registry to see available wikis."
- If exactly one candidate: use it directly. Set `wiki_path = <candidate-path>`.
- If multiple candidates:
  - Check for a cached inference result from earlier in this conversation. The cache is conversation-scoped only: remember the chosen wiki name within the current Claude conversation. Do not create any file, environment variable, or persistent storage for the cache. If you have already resolved a wiki via inference or user choice in this conversation, reuse that resolution here without re-running inference. **Cache invalidation:** If CWD has changed since the wiki was cached, invalidate the cache and re-resolve from Sub-step 0.3.
  - Otherwise, dispatch the inference subagent (see Sub-step 0.8). Cache the result.

**Sub-step 0.5b: Validate the resolved wiki**

Before proceeding, verify `<wiki_path>/schema.md` exists and is readable. If not: STOP. Report: "Wiki at '<wiki_path>' is missing schema.md. The wiki may be corrupted." This prevents downstream steps from failing with confusing errors.

**Sub-step 0.6: Touch the registry (write skills only)**

For write operations (wiki-add, wiki-absorb, wiki-bootstrap, wiki-reorg), update the `last_used` field for the resolved wiki to today's date. Use the atomic write pattern.

For read-only skills (wiki-query, wiki-health in full/audit/dry-run modes), SKIP this sub-step entirely — do not write to the registry on reads.

**Sub-step 0.7: Atomic write pattern**

For every registry mutation:
1. Read `~/.claude/wikis.json` fresh into memory.
2. Apply the mutation in memory.
3. Write the serialized JSON to `~/.claude/wikis.json.tmp` using the Write tool.
4. Use the Bash tool to rename: `mv ~/.claude/wikis.json.tmp ~/.claude/wikis.json`

The POSIX rename is atomic. Concurrent writers may lose each other's changes (last-writer-wins), but the file never becomes unparseable mid-write.

**Sub-step 0.8: Inference mechanics**

When inference is needed, dispatch a ONE-SHOT Agent call (NOT a full Analyst/Writer/Reviewer cycle):

    Agent tool:
      description: "wiki-<skill-name> -- Inference phase"
      prompt: |
        You are picking the most relevant wiki for a user command.

        ## Candidate Wikis
        [for each candidate: name, description, last_used]

        ## User Message
        [the user's current message verbatim]

        ## Recent Conversation Context
        [last 3-5 messages from the conversation, or "No prior context" if session is fresh]

        ## Your Job
        Return exactly one of:
        - CONFIDENT: <name> — if one wiki clearly matches based on name mentions, description keywords, or recent context
        - AMBIGUOUS: <name1>, <name2>, <name3> — if 2-3 wikis plausibly match

        Do not explain your reasoning. Output only the classification line.

Parse the response:
- `CONFIDENT: <name>` → use that wiki. Set `wiki_path` and remember this choice in the current conversation so subsequent wiki commands in this conversation reuse it without re-running inference.
- `AMBIGUOUS: ...` → present to user: "Which wiki? [list with descriptions]". Wait for user choice. Cache the choice for the session.

**Sub-step 0.9: Write Session Cache**

After full discovery completes (Sub-steps 0.1-0.8), write `<wiki_path>/.wiki-resolved` with the discovery results:

```
wiki_path: <absolute path>
schema_domain: <domain from schema.md>
article_count: <count>
resolved_at: <ISO timestamp>
```

This cache is valid for the current session only. It will be ignored if older than 4 hours.

**After Step 0 completes:** `wiki_path` is the canonical absolute path to the resolved wiki. All subsequent steps use `<wiki_path>/` wherever the skill previously used `wiki/`.
