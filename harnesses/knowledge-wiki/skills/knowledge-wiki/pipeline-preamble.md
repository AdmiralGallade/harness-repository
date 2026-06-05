<!-- Shared preamble for wiki pipeline subagents (writer + reviewer prompts) -->
<!-- Referenced by: wiki-absorb, wiki-add, wiki-bootstrap, wiki-reorg -->
<!-- SSOT for wiki-path resolution and tool usage conventions -->

## Wiki Path

**IMPORTANT — Wiki Path:** The Runtime Context will include a `### Wiki Path` field containing the absolute path to the target wiki directory. All file paths below use `<wiki_path>` as a placeholder. Replace it with the actual path from Runtime Context when reading or writing files. Do NOT use the literal path `wiki/` — that was the old single-wiki convention.

## Tool Usage

- Use the **Write** tool to create new files. Do NOT use Bash echo/cat.
- Use the **Edit** tool to modify existing files. Do NOT use Bash sed/awk.
- Use the **Read** tool to read files. Do NOT use Bash cat/head/tail.
- Use the **Glob** tool to find files. Do NOT use Bash find/ls.
- Use the **Grep** tool to search content. Do NOT use Bash grep/rg.
