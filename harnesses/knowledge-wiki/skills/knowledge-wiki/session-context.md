[project-wiki] Wiki framework active.

REGISTERED WIKIS: Read ~/.claude/wikis.json at session start to discover available wikis. If the file does not exist, no wikis are registered yet — an unregistered `./wiki/schema.md` in CWD will be auto-registered on first write command.

WIKI SELECTION:
- User explicit: --wiki <name> flag
- CWD-scoped: automatic if one registered wiki matches current directory
- Inference: used when multiple wikis match CWD or conversation mentions a wiki name
- Auto-register: first-time setup when ./wiki/schema.md exists but is unregistered

WORKFLOW: add → absorb → query/health → reorg
EPISODIC WORKFLOW: episodic entries → consolidate (5+ entries) → inbox → absorb → articles

WHEN TO ACT:
- Solved a problem or learned something? → /wiki-add
- Added reference docs? → /wiki-add --file or /wiki-add --url
- Inbox has 3+ items? → /wiki-absorb
- Domain question? → /wiki-query
- Wiki empty or thin? → /wiki-bootstrap
- 5+ unconsolidated episodic entries? → /wiki-consolidate
- Periodic health check? → /wiki-health --audit-only
- Articles going stale? → /wiki-health --mark-stale
- Want to see all wikis? → /wiki-registry
- Rename a wiki? → /wiki-registry rename <old> <new>
- Adopt an existing wiki directory? → /wiki-init --register <path>

RED FLAGS:
- "I'll capture this later" → You won't. /wiki-add now.
- "This insight is too small" → Atomic articles are the goal.
- "The wiki already covers this" → /wiki-query first — you might be wrong.
- "The wiki needs more content first" → /wiki-bootstrap solves this.

NEVER skip absorb. Inbox entries are invisible to query/health/reorg.

SUBAGENT PATTERN: All write operations use Analyst → Writer → Reviewer.
HYBRID: /wiki-consolidate uses Python pre-pass (consolidate.py scan/mark) + A→W→R.
SINGLE-SHOT: /wiki-registry (list + rename), /wiki-health (diagnostic + dashboard + staleness).
