<!-- Convention version: 2026-04-20 -->
# Research Loop Specification

Full protocol for Step 2.5 (Research Phase) of wiki-bootstrap. Referenced from SKILL.md.

## Ceremony-Level Detection

Read ceremony level from `.dev-wiki/config.md` (`ceremony:` field) or from the phase frontmatter if accessible. Set research budgets:

| Parameter | Standard | Lite |
|-----------|----------|------|
| max_rounds | 5 | 1 |
| max_dispatches | 30 | 5 |
| coverage_threshold | 90% | 70% |
| min_sources | 3 | 1 |

Default to **Standard** if ceremony level is unknown or unreadable.

## Note Directory Lifecycle

- **Before round 1:** Create `<wiki_path>/.bootstrap-research/`
- **If directory already exists** (interrupted prior run): verify path ends in `.bootstrap-research` before clearing (`rm -rf` then recreate). Never delete a path that does not match this suffix.
- **After writer completes** (Step 4): verify path ends in `.bootstrap-research`, then delete: `rm -rf <wiki_path>/.bootstrap-research/`

## Research Loop (rounds 1 to max_rounds)

For each round:

1. **Read prompt:** Read `research-agent-prompt.md` from this skill's directory
2. **Partition questions:** Partition the analyst's Research Questions across topic clusters (from the analyst's Research Plan). Each cluster gets 3-5 related questions.
3. **Dispatch subagents:** Build a cumulative `previously_seen_sources` set from all prior-round notes (extract all `**Source:** <URL>` entries). Dispatch 3-5 parallel research subagents via Agent tool, each receiving:
   - The `research-agent-prompt.md` content
   - Their assigned topic cluster + question subset
   - Round number
   - Note write path pattern: `<wiki_path>/.bootstrap-research/r<round>-<cluster-slug>.md`
   - Prior round note paths (if round > 1)
   - The `previously_seen_sources` URL set (subagents must not re-cite these)
4. **Compute coverage** after all subagents complete:
   - Read all notes in `.bootstrap-research/`
   - For each question in Q: count distinct sources cited. A question is "covered" if sources >= min_sources
   - coverage = covered_questions / |Q|
5. **Check OR-gate exit conditions** (ANY triggers exit):
   - coverage >= coverage_threshold
   - round == max_rounds
   - No new sources found this round (all subagents returned 0 new findings)
   - Total dispatches across all rounds >= max_dispatches
6. **If exiting:** report coverage stats, list unfillable gaps
7. **If continuing:** identify under-covered questions, dispatch targeted follow-up subagents for gaps only

## Gap Passing

Questions that remain uncovered after the loop exits are passed to the writer step (Step 4) with the flag: "seeded from training knowledge -- verify for accuracy"

## Coverage Report

After the loop, print:

```
Research complete: coverage X% (Y/Z questions covered, N rounds, D dispatches)
Gaps: [list of uncovered question IDs, or "none"]
```
