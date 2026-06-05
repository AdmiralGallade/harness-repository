# Reflexive Claude Code

> **Attribution:** This harness is sourced from [wayne930242/reflexive-claude-code](https://github.com/wayne930242/Reflexive-Claude-Code) by [@wayne930242](https://github.com/wayne930242), used under the open-source License. No modifications have been made to the original files.

[English](README.md) | [ç¹é«”ä¸­æ–‡](README.zh-TW.md)

A Claude Code plugin marketplace for **skills-driven Agentic Context Engineering (ACE)** â€” build, analyze, and maintain agent systems with structured workflows.

## What This Does

Reflexive Claude Code gives Claude Code a complete toolkit for managing its own agent system: CLAUDE.md, rules, skills, subagents, and hooks. Every component follows a structured creation process with automated quality review.

**Key capabilities:**

- **Build agent systems from scratch** â€” detect project maturity, explore workflows, plan architecture, then create all components in dependency order
- **Analyze existing systems** â€” 11-category weakness checklist covering routing, context management, security, rules health, and cross-tool migration
- **Validate on every edit** â€” PostToolUse hook checks frontmatter, broken links, orphaned files, and invalid variables in real time
- **Enforce quality gates** â€” 5 specialized reviewer agents (skill, CLAUDE.md, rule, hook, subagent) run after every creation or modification
- **Advanced security architecture** â€” AI-specific security patterns, eight-layer defense system, 30-second performance constraints, and intelligent reflection-driven learning

## Installation

```bash
/plugin marketplace add wayne930242/Reflexive-Claude-Code
/plugin install rcc@rcc          # core ACE workflow
/plugin install aref@rcc         # agentic refactoring pipeline (optional, independent)
```

Both plugins live in the same marketplace. Install whichever you need; they coexist and are independently versioned.

## How It Works

### Agent System Pipeline

The full pipeline runs through 6 stages, each a dedicated skill:

```
migrate â†’ analyze â†’ brainstorm â†’ plan â†’ apply â†’ review â†’ refactor
```

| Stage | Skill | What it does |
|-------|-------|-------------|
| **Migrate** | `migrating-agent-systems` | Detect maturity (None/Seed/Partial/Established), propose rules refactoring, route to correct chain |
| **Analyze** | `analyzing-agent-systems` | Scan all components, run 11-category weakness checklist, produce Rules Health Summary |
| **Brainstorm** | `brainstorming-workflows` | Explore workflows with complexity ladder (L1-L6), map to Anthropic patterns |
| **Plan** | `planning-agent-systems` | Architecture flowchart first, then dependency-driven component plan |
| **Apply** | `applying-agent-systems` | Invoke writing-* skills in order: CLAUDE.md â†’ rules â†’ hooks â†’ skills â†’ agents |
| **Review** | `reviewing-agent-systems` | Run all 5 reviewer agents, produce structured report |

### Quality Checks

**11-category weakness analysis** (via `analyzing-agent-systems`):

| # | Category | Key checks |
|---|----------|-----------|
| 1 | Routing / Triggers | Vague descriptions, overlapping triggers, missing handoffs |
| 2 | Context Management | Oversized CLAUDE.md, eager loading, context pollution |
| 3 | Workflow Continuity | Broken chains, missing verification gates |
| 4 | Redundancy / Conflicts | Duplicate rules, contradicting instructions |
| 5 | Security / Safety | Unprotected sensitive files, excessive permissions |
| 6 | Observability | Missing structured output, opaque routing |
| 7 | Architecture / Scaling | Flat topology, over-orchestration |
| 8 | Constitution Stability | Procedures in CLAUDE.md, vague instructions |
| 9 | Project Context | Missing deployment docs, language coverage gaps |
| 10 | Cross-Tool Migration | Unimported `.cursorrules`, copilot instructions |
| 11 | Rules Health | Lines > 50, missing `paths:`, dead globs, session-start > 300 lines |

**Rules Health Summary** (produced during analysis):

| Metric | Threshold |
|--------|-----------|
| CLAUDE.md lines | > 200 = warning |
| Session-start total (CLAUDE.md + global rules) | > 300 = warning |
| Individual rule lines | > 50 = warning |
| Path-scoped rule with 0 file matches | dead glob |
| Procedural content in rules | should be a skill |

**Real-time validation hook** (`validate_frontmatter.py`):
- Fires on every Edit/Write to skill, agent, or rule files
- Checks for invalid frontmatter fields against official spec
- Detects broken markdown links and orphaned files in skill directories
- Outputs `additionalContext` so Claude can self-correct immediately

### Component Writing Skills

Each `writing-*` skill follows a structured process with a reviewer gate:

| Skill | Creates | Reviewer |
|-------|---------|----------|
| `writing-claude-md` | `CLAUDE.md` | `claudemd-reviewer` |
| `writing-rules` | `.claude/rules/*.md` | `rule-reviewer` |
| `writing-hooks` | `.claude/hooks/*` | `hook-reviewer` |
| `writing-skills` | `.claude/skills/*/SKILL.md` | `skill-reviewer` |
| `writing-subagents` | `.claude/agents/*.md` | `subagent-reviewer` |

### Plugin Pipeline

Separate pipeline for creating and maintaining Claude Code plugins:

```
migrate-plugin â†’ validate â†’ refactor
                 â†‘
        (or) create from scratch / convert from scripts
```

| Maturity | Detection | Route |
|----------|-----------|-------|
| **None** | No `.claude-plugin/` | â†’ `creating-plugins` (from scratch) |
| **Pre-plugin** | Script project without plugin structure | â†’ Propose conversion table â†’ `creating-plugins` (with proposal) |
| **Minimal** | Has manifest, missing components | â†’ `validating-plugins` â†’ `refactoring-plugins` |
| **Complete** | Full plugin | â†’ `validating-plugins` â†’ `refactoring-plugins` |

### Skill Assets

Each skill can bundle three types of supporting assets:

| Directory | Role | Example |
|-----------|------|---------|
| `references/` | Documentation Claude reads on demand | Checklists, pattern catalogs |
| `scripts/` | Executable automation | Scaffolders, validators |
| `templates/` | Reusable file skeletons | Report formats, config files |

The planner decides which assets each skill needs; the reviewer checks they exist; the refactorer creates missing ones directly.

### Model Recommendations

**Primary orchestrator: `claude-opus-4-7`** â€” per Anthropic's [Opus 4.7 prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Opus 4.7 is the recommended main model for long-horizon agentic work, subagent orchestration, and coding. Start at `xhigh` effort for coding/agentic use cases; minimum `high` for intelligence-sensitive work. Set `max_tokens` â‰¥ 64k at `xhigh`/`max` so the model has room to think and act.

| Use Case | Model | Effort |
|----------|-------|--------|
| Main orchestrator, long-horizon agentic, planning | `claude-opus-4-7` | `xhigh` / `high` |
| Implementation, code generation | `sonnet` | `high` |
| Read-only analysis, review | `sonnet` | `medium` |
| Simple lookup, exploration | `haiku` | `low` |

## Full Skill List

### rcc (v11.2.0) <!-- x-release-please-version -->

| Skill | Purpose |
|-------|---------|
| `migrating-agent-systems` | Maturity-graded routing with rules refactoring proposal |
| `migrating-plugins` | Plugin maturity detection (None/Pre-plugin/Minimal/Complete), script-to-plugin conversion |
| `analyzing-agent-systems` | Project scanning + 11-category weakness detection + actionable restructuring recommendations |
| `brainstorming-workflows` | Targeted exploration of pipeline modes, pain points, and routine tasks |
| `planning-agent-systems` | Architecture-first planning with dependency ordering |
| `applying-agent-systems` | Execute component plan via writing-* chain |
| `reviewing-agent-systems` | Run all 5 reviewer agents |
| `refactoring-agent-systems` | Fix issues from review report |
| `writing-skills` | Structured skill creation |
| `writing-claude-md` | CLAUDE.md with standard format |
| `writing-subagents` | Subagent config with model/isolation guide |
| `writing-rules` | Rules with decision tree and content validation |
| `writing-hooks` | Hooks for static analysis and quality gates |
| `reflecting` | Extract learnings, route to skills or rules |
| `improving-skills` | Optimize a single skill |
| `refactoring-skills` | Consolidate and deduplicate across skills |
| `advising-architecture` | Classify knowledge type, validate approach |
| `initializing-projects` | Bootstrap new project with agent system |
| `creating-plugins` | Scaffold a new Claude Code plugin |
| `refactoring-plugins` | Health-check plugins against official best practices |
| `validating-plugins` | Batch scan all plugin files for errors |

### aref (v0.2.0)
<!-- aref version is manually synced from plugins/aref/.claude-plugin/plugin.json â€” release-please cannot scope generic markers per package -->


Agentic refactoring pipeline. Detects languages, analyzes hotspots, proposes phased refactor plans, scaffolds characterization tests, applies refactors on a dedicated branch with per-phase review, verifies against hard structural rules and mutation testing, then writes AGENTS.md per subproject for future AI coding agents.

**Entry command:** `/aref`

**Pipeline:** analyzing-codebases â†’ planning-refactors â†’ scaffolding-characterization-tests â†’ applying-refactors â†’ verifying-refactors â†’ finalizing-refactors

**Supported languages:** TypeScript/JavaScript, Python, Rust, Go (deep). Other languages fall back to generic analysis.

See [plugins/aref/README.md](./plugins/aref/README.md) for full details.

## Project Structure

```
Reflexive-Claude-Code/
â”œâ”€â”€ .claude-plugin/
â”‚   â””â”€â”€ marketplace.json
â”œâ”€â”€ .rcc/                     # Per-project RCC artifacts (tracked)
â”‚   â”œâ”€â”€ config.yml            # Migration state + decisions log
â”‚   â”œâ”€â”€ {timestamp}-*.md      # analysis / plan / reflection / review outputs
â”‚   â”œâ”€â”€ memory/               # learning-from-failures knowledge
â”‚   â”œâ”€â”€ validation/           # validate_all.py reports
â”‚   â””â”€â”€ archive/              # refactor-sweep snapshots
â”œâ”€â”€ plugins/
â”‚   â””â”€â”€ rcc/
â”‚       â”œâ”€â”€ skills/           # 21 skills
â”‚       â”œâ”€â”€ agents/           # 5 reviewer subagents
â”‚       â””â”€â”€ hooks/            # Frontmatter validation hook
â”œâ”€â”€ release-please-config.json
â”œâ”€â”€ .release-please-manifest.json
â””â”€â”€ README.md
```

### `.rcc/config.yml`

Every RCC-enabled project carries `.rcc/config.yml` recording:

- Migration state (when last migrated, which rcc version)
- Release automation decision (release-please / semantic-release / declined)
- Settings scope (where safety bypass / permission rules live: `.claude/settings.json` vs `.claude/settings.local.json` vs `~/.claude/settings.json`)
- Primary model assignments (orchestrator / implementer / reviewer)
- Append-only `decisions_log`

Managed by `migrating-agent-systems` (creation) and `reflecting` (log append). See [config schema](plugins/rcc/skills/migrating-agent-systems/references/config-schema.md).

## Credits

- **[superpowers](https://github.com/anthropics/claude-code-superpowers)** â€” TDD-based skill design and discipline-enforcing patterns adapted from Anthropic's superpowers plugin.
- **Agentic Context Engineering (ACE)**:
  > Zhang, Q., et al. (2025). *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models*. arXiv:2510.04618.

## License

MIT

