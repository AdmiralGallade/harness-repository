---
name: wiki-registry
description: "Use when listing or renaming registered wikis. Default mode lists all wikis. Use 'rename <old> <new>' to change a wiki's display name. Read-only for listing; registry-write for rename. Do NOT use for detailed wiki health — use wiki-health."
---

# wiki-registry

Manage the wiki registry (`~/.claude/wikis.json`). Two modes: list (default) and rename.

---

## Mode Detection

| Invocation | Mode | Behavior |
|------------|------|----------|
| `/wiki-registry` | list | Show all registered wikis (read-only) |
| `/wiki-registry rename <old> <new>` | rename | Change a wiki's display name |

**Aliases (backward-compatible):**
- `/wiki-list` routes to `/wiki-registry`
- `/wiki-rename <old> <new>` routes to `/wiki-registry rename <old> <new>`

---

## Pre-checks (both modes)

1. **Registry readable:** Read `~/.claude/wikis.json`. If not found: "No wikis registered yet. Run `/wiki-init` to create one, or `/wiki-init --register <path>` to adopt existing." Stop.
2. **Registry parseable:** If corrupted JSON: "Registry at ~/.claude/wikis.json is corrupted. Back up and remove it, then re-register with /wiki-init --register <path>." Stop.

### Rename mode additional pre-checks

3. **Two arguments:** Requires `<old-name> <new-name>`. If missing: "Usage: `/wiki-registry rename <old-name> <new-name>`." Stop.
4. **Old name exists:** Look up `<old-name>` in wikis array. If not found: "No wiki named '<old-name>'. Run `/wiki-registry` to see available." Stop.
5. **New name unique:** No existing entry with `name == <new-name>`. If collision: "A wiki named '<new-name>' already exists." Stop.
6. **New name format:** Must be kebab-case (lowercase, digits, hyphens, no leading/trailing/consecutive hyphens). If invalid: "Wiki names must be kebab-case. '<new-name>' is invalid." Stop.

---

## List Mode

### Step 1: Read registry
Parse `~/.claude/wikis.json` and extract the `wikis` array. If empty: "No wikis registered. Run `/wiki-init` to create one." Stop.

### Step 2: Gather article counts
For each wiki:
1. Verify `path` exists on disk. If not, mark as "missing".
2. Count `.md` files under `<path>/articles/**/*.md` (exclude schema.md, index.md, log.md).

### Step 3: Format and report

```
Registered wikis (N):

| Name | Description | Path | Articles | Last Used |
|------|-------------|------|----------|-----------|
| ... | ... | ... | ... | ... |

Run `/wiki-registry rename <old> <new>` to rename a wiki.
Run `/wiki-init --register <path>` to add an existing wiki.
```

Sort by `last_used` descending, then name ascending.

---

## Rename Mode

### Step 1: Read registry
Parse `~/.claude/wikis.json`.

### Step 2: Update name
Find entry where `name == <old-name>`, change to `<new-name>`. Leave path, description, registered, last_used unchanged.

### Step 3: Atomic write
1. Serialize to JSON (2-space indent).
2. Write to `~/.claude/wikis.json.tmp`.
3. Rename: `mv ~/.claude/wikis.json.tmp ~/.claude/wikis.json`.

### Step 4: Report
```
Renamed '<old-name>' to '<new-name>'.
Path unchanged: <path>
```

---

## Error Handling

- Read failures: "Could not read ~/.claude/wikis.json: [error]."
- Write failures (rename mode): "Rename failed: [error]. Registry unchanged." Note if .tmp file needs cleanup.
- Never attempt automatic recovery.
