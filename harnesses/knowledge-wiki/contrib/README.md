# Contrib — Deferred Skills

These skills are functional but not part of the core skill suite. They were deferred during consolidation to reduce the active command surface.

To enable a deferred skill, copy its directory to your Claude Code skills folder:

```bash
cp -r contrib/wiki-synthesize ~/.claude/skills/wiki-synthesize
```

## Deferred Skills

### wiki-synthesize

Creative synthesis skill that generates new insights by connecting existing wiki articles. Requires 5+ articles. Produces speculative content at `draft` status.

Deferred because: creative generation rather than knowledge management; no clear integration with the episodic→consolidate→absorb pipeline; low usage frequency.
