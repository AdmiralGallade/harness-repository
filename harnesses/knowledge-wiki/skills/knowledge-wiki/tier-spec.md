<!-- Canonical tier definitions — SSOT for all wiki skills -->
<!-- REFERENCE, DO NOT PASTE. Skills that handle tier logic should link here rather than duplicate definitions. -->

# Wiki Article Tiers

Three-tier model for wiki content. The model is architecturally three-tier (episodic, public, private) but only `public` and `private` appear as frontmatter values — episodic entries are implicit by directory (`episodic/`) and follow `episodic-conventions.md`, not the article frontmatter schema.

## Tier Definitions

| Tier | Semantics | Who Writes | Modifiable | Verification |
|------|-----------|------------|------------|--------------|
| `episodic` | What happened — session logs, task traces, research findings, worker outputs | Any caller (Claude Code, Nanaclaw, Qwen) | Append-only, never modified after creation | None required |
| `public` | Domain facts — should be verifiable, citable, shareable | Absorb, bootstrap, consolidate | Yes, through absorb/reorg | Source-credibility verifier for high-density claims |
| `private` | Personal analysis — trading theses, subjective assessments, decisions without external validation | wiki-add (capture), manual | Yes, through wiki-add/reorg | None required |

## Tier Assignment Rules

| Skill | Default Tier | Rationale |
|-------|-------------|-----------|
| wiki-absorb | Analyst classifies as `public` or `private` based on content | Absorbed articles may contain either factual or personal content |
| wiki-bootstrap | Always `public` | Bootstrap produces domain facts from research |
| wiki-add (capture) | Default `private`, user may override | Session captures are personal analysis by default |
| wiki-add (ingest) | `public` for external refs, `private` for personal notes | Source type determines tier |
| synthesize (contrib) | Inherits dominant tier from source articles | Synthesis of public articles is public; mixed defaults to private |
| wiki-consolidate | Inherits from episodic source classification | Consolidation extracts facts from episodic entries |

## Frontmatter

Articles use `tier:` in frontmatter:

```yaml
tier: public | private
```

Episodic entries do NOT use the `tier` field — they are implicitly episodic by virtue of living in `episodic/`. See `episodic-conventions.md` for their frontmatter format.

## Migration

For existing articles created before the tier model: default to `tier: public`, `status: reviewed` (they passed the reviewer subagent already).

## Validation

- wiki-health check 11 (Tier Validity): every article must have `tier` field with value `public` or `private`. Severity: ERROR.
- Episodic entries are exempt from article-level lint checks.
