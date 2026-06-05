# knowledge-wiki

> **Attribution:** This harness is sourced from [j-wanger/knowledge-wiki](https://github.com/j-wanger/knowledge-wiki) by [@j-wanger](https://github.com/j-wanger), used under the MIT License. No modifications have been made to the original files.

A Claude Code skill suite for managing persistent knowledge bases. Provides a complete CRUD lifecycle for wiki-style knowledge stores: add insights and external material, absorb raw entries into polished articles, query across articles, and maintain structural health.

## What it does

- **Add** decisions, patterns, lessons from conversations or external files/URLs into a structured wiki
- **Absorb** raw inbox entries into polished, cross-linked articles
- **Query** the wiki for answers using article navigation and synthesis
- **Bootstrap** new wikis from online research or seed existing ones with new topics
- **Maintain** wiki health with auditing, staleness detection, and reorganization

## Skills

| Skill | Purpose |
|-------|---------|
| `/knowledge-wiki` | Router — dispatches to the correct sub-skill based on user intent |
| `/wiki-init` | Bootstrap a new wiki with schema, directory structure, and initial articles |
| `/wiki-add` | Add to inbox — capture conversation insights or ingest external files/URLs |
| `/wiki-absorb` | Convert raw inbox entries into polished, cross-linked articles |
| `/wiki-query` | Answer questions by navigating and synthesizing wiki articles |
| `/wiki-bootstrap` | Seed a wiki via online research (full gap analysis or focused topics) |
| `/wiki-health` | Dashboard metrics, structural audit (13 checks), and staleness marking |
| `/wiki-reorg` | Restructure categories, fix hierarchy, garden the wiki |
| `/wiki-consolidate` | Convert episodic entries into inbox entries via dedup + fact extraction |
| `/wiki-index` | Build hybrid search index (FTS5 + vector) for faster wiki-query |
| `/wiki-registry` | List all registered wikis or rename one |

See `contrib/` for deferred skills (wiki-synthesize).

## Installation

Copy the skill directories to your Claude Code skills folder:

```bash
# Clone
git clone https://github.com/j-wanger/knowledge-wiki.git
cd knowledge-wiki

# Copy to Claude Code skills directory
cp -r skills/* ~/.claude/skills/
```

## Usage

```
# Start a new wiki for your project
/wiki-init

# Capture an insight from conversation
/wiki-add

# Import reference material
/wiki-add --file docs/reference.md
/wiki-add --url https://example.com/guide

# Process inbox entries into articles
/wiki-absorb

# Ask the wiki a question
/wiki-query

# Check wiki health (dashboard + audit)
/wiki-health

# Research and add new content
/wiki-bootstrap
```

## Wiki structure

Each wiki follows this layout:

```
wiki/
  schema.md          # Domain identity, tags, hierarchy roots
  index.md           # Article index by category and hierarchy
  inbox/             # Raw captures awaiting absorb
  episodic/          # Append-only session logs and worker outputs
  articles/
    concepts/        # Core domain concepts
    patterns/        # Reusable patterns and techniques
    decisions/       # Architectural Decision Records
    action-plans/    # Improvement plans with tracked progress
```

## Multi-wiki support

Register multiple wikis in `~/.claude/wikis.json`. Each wiki is scoped to a project directory and automatically activated when Claude Code's working directory matches.

## Package contents

- 11 skill directories (1 router + 10 sub-skills)
- ~66 files, ~6,500 lines
- Hybrid search index (FTS5 + vector) via wiki-index — requires Python 3.11+, uv, fastembed, sqlite-vec, xxhash
- Document-to-markdown conversion via convert.py — tiered engines (Kreuzberg, Docling, Pandoc) for PDF, DOCX, PPTX, XLSX, images
- Consolidation pipeline via wiki-consolidate — converts episodic entries into inbox entries with dedup
- Three-tier content model (public/private/episodic) with five-state article lifecycle

## Development

```bash
# Install dev dependencies (uv.lock is committed for reproducibility)
uv sync --group dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Run with optional vector dependencies
uv sync --group dev --group vectors
```

## Related

- [dev-wiki](https://github.com/j-wanger/dev-wiki) — Project lifecycle management (phases, tasks, reviews)
