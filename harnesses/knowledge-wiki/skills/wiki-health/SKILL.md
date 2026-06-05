---
name: wiki-health
description: "Use for wiki health checks: dashboard metrics, structural audit, and staleness marking. Default mode shows full report. Use --audit-only for structural checks only, --mark-stale to detect and mark stale articles. Do NOT use for dev wiki validation (use dev-check) or for fixing issues (use wiki-reorg)."
---

# wiki-health

Combined wiki health tool: dashboard metrics (from wiki-status), structural audit (from wiki-lint), and staleness marking (from wiki-stale). Single-agent, single-pass architecture — scans articles once, produces all outputs from the same data.

---

## Mode Detection

| Invocation | Mode | Behavior |
|------------|------|----------|
| `/wiki-health` | full | Dashboard + structural audit (read-only) |
| `/wiki-health --audit-only` | audit | Structural audit only, skip dashboard (read-only) |
| `/wiki-health --mark-stale` | mark | Detect stale articles and update their status (writes) |
| `/wiki-health --mark-stale --dry-run` | dry-run | Staleness report without marking (read-only) |

**Aliases (backward-compatible):**
- `/wiki-lint` routes to `/wiki-health --audit-only`
- `/wiki-status` routes to `/wiki-health`
- `/wiki-stale` routes to `/wiki-health --mark-stale`
- `/wiki-stale --dry-run` routes to `/wiki-health --mark-stale --dry-run`

---

## Step 0: Resolve Wiki

Read and follow `~/.claude/skills/knowledge-wiki/step-0-template.md`.

- **Full/audit/dry-run modes** are read-only — SKIP Sub-step 0.6 (no `last_used` touch).
- **--mark-stale mode** (without --dry-run) is a write operation — update `last_used` in Sub-step 0.6.

---

## Pre-checks

1. **wiki exists:** If `<wiki_path>` does not exist: "Wiki path does not exist: <wiki_path>. The registry may be stale. Run `/wiki-registry`." Stop.
2. **articles exist:** If `<wiki_path>/articles/` is empty or missing: "Wiki has no articles yet. Run `/wiki-add` to add content, then `/wiki-absorb` to process it." Stop (audit/mark modes). For full mode: show minimal dashboard with zero counts and stop.

---

## Step 1: Single-Pass Article Scan

Scan all `.md` files under `<wiki_path>/articles/` recursively. For each article, collect:
- File path, line count, body text
- Frontmatter: title, aliases, category, tags, parents, created, updated, source, tier, status
- All `[[link]]` references in body
- Staleness eligibility (status = verified or reviewed)

Also scan:
- `<wiki_path>/inbox/` for pending entry count
- `<wiki_path>/episodic/` for episodic entry count and consolidation status
- `<wiki_path>/schema.md` for domain, custom tags, hierarchy roots, staleness_rules
- `<wiki_path>/index.md` for index entries
- `<wiki_path>/log.md` for recent activity (last 5)

---

## Step 2: Dashboard (skip if --audit-only or --mark-stale)

Read `dashboard-spec.md` for the full format and metric computation rules. Produce the dashboard from Step 1 data.

---

## Step 3: Structural Audit (skip if --mark-stale without full/audit)

Run ALL 13 checks on the data collected in Step 1.

### 1. Broken Links
For each `[[link]]` in article bodies, verify a matching `.md` exists under `<wiki_path>/articles/`.
Severity: **ERROR**

### 2. Orphaned Articles
Articles with zero inbound `[[links]]` from other articles.
Severity: **WARNING**

### 3. Bloated Articles
Articles exceeding 120 lines.
Severity: **WARNING**

### 4. Stub Articles
Articles with fewer than 15 lines.
Severity: **WARNING**

### 5. Missing Tags
Tags used by 3+ articles but not in `schema.md` Custom Tags section.
Severity: **INFO**

### 6. Dead Tags
Tags in `schema.md` used by zero articles.
Severity: **INFO**

### 7. Frontmatter Issues
Missing required fields (title, aliases, category, tags, parents, created, updated, source, tier, status). Invalid category values.
Severity: **ERROR**

### 8. Parent Consistency
Parents in frontmatter without matching `[[link]]` in Related section, or inconsistent bidirectional relationships.
Severity: **WARNING**

### 9. Index Drift
Articles on disk not in index, or index entries pointing to missing files.
Severity: **ERROR**

### 10. Duplicate Topics
Articles with identical/near-identical titles or overlapping aliases.
Severity: **INFO**

### 11. Tier Validity
Missing or invalid `tier` field (must be `public` or `private`). Episodic entries exempt.
Severity: **ERROR**

### 12. Status Validity
Missing or invalid `status` field (must be draft/reviewed/verified/stale/archived).
Severity: **ERROR**

### 13. Staleness Detection
For articles with status verified or reviewed, compute `days_since_update = today - updated`. Apply staleness_rules from schema (tag overrides use shortest-wins per `lifecycle-spec.md`). Default 180 days if unconfigured. Flag articles past threshold.
Severity: **WARNING**

### Empirical-Anchor Density (Advisory)
Read `empirical-anchor-spec.md`. Apply to concept/pattern articles. Strictly INFO.

### Report Format

```
Wiki Audit Report -- YYYY-MM-DD

ERRORS (must fix):
- [check name]: [specific finding]

WARNINGS (should fix):
- [check name]: [specific finding]

INFO:
- [check name]: [specific finding]

Summary: N errors, M warnings, K info
```

If all checks pass: "Wiki health: All checks passed. No issues found."

---

## Step 4: Mark Stale Articles (--mark-stale mode only)

Uses staleness computation from Step 1/check 13.

**--dry-run:** Present staleness report and STOP:
```
Wiki Staleness Report -- YYYY-MM-DD (<wiki_name>)
STALE: <title> (updated: YYYY-MM-DD, threshold: Nd, elapsed: Nd)
OK: <title> (updated: YYYY-MM-DD, threshold: Nd, remaining: Nd)
Summary: N stale, M ok
```

**Without --dry-run:** For each stale article, read-modify-write:
1. Read full file.
2. Edit: replace `status: verified` or `status: reviewed` with `status: stale`.
3. Do NOT modify other frontmatter fields or article body.

Emit per article: "Marked stale: <title> (<path>)"

Append to `<wiki_path>/log.md`:
```
[YYYY-MM-DDTHH:MM:SS] STALE -- N articles marked stale, M within threshold
```

---

## Step 5: Remediation Suggestions (full and audit modes)

After the report, suggest which commands fix each issue type:

- **Broken links, orphans, structural issues**: "Run `/wiki-reorg` to fix."
- **Index drift (new articles)**: "Run `/wiki-absorb` to process."
- **Index drift (restructuring)**: "Run `/wiki-reorg` to rebuild."
- **Tag issues**: "Review `schema.md` Custom Tags section."
- **Frontmatter issues**: "Edit affected files directly."
- **Bloated articles**: "Run `/wiki-reorg` to split."
- **Stubs**: "Flesh out or merge via `/wiki-reorg`."
- **Stale articles**: "Run `/wiki-health --mark-stale` to mark, then review or archive."

---

## Strictly Read-Only (full/audit/dry-run modes)

These modes do NOT modify any files. Only `--mark-stale` (without `--dry-run`) writes to article frontmatter and log.md.

---

## Size Rationale

This skill exceeds the 250-line cap at ~300 lines. Justified: merges 3 former skills (wiki-lint 277 lines, wiki-status 253 lines, wiki-stale 78 lines) into a single-pass architecture. Dashboard metrics extracted to `dashboard-spec.md` companion. Single invocation per session.
