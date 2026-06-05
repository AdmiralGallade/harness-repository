# import-harness

Import an external Claude Code harness into this repository and register it in `harnesses.json`.

## Trigger

Use this skill when the user wants to add a new harness to the harness repository from a GitHub repository or a local directory. Phrases like "add harness from", "import harness", "add this repo as a harness" should trigger it.

## Steps

### 1 — Gather inputs

Ask the user for:
- **Source**: a GitHub URL (e.g. `https://github.com/owner/repo`) or an absolute local path to the downloaded/cloned repo
- **Harness ID**: a short kebab-case identifier (e.g. `dev-wiki`). Suggest one derived from the repo name.
- **Description**: a one-sentence description of what the harness does.
- **Category**: a single word (e.g. `workflow`, `data`, `migration`, `tooling`).
- **Tags**: comma-separated keywords.
- **Attribution / author credit**: the original author and source URL. Prepopulate from the GitHub URL when available (format: `owner (https://github.com/owner/repo)`).

If the source is a GitHub URL, tell the user to clone or download it locally first, then provide the local path. Do not attempt to clone automatically.

### 2 — Locate the repository root

The harness repository lives at:
```
C:\Users\mailf\OneDrive\Documents\GitHub\harness-repository\harness-repository\
```

The target harness folder will be:
```
harnesses/<harness-id>/
```

### 3 — Copy source files

Copy the entire source directory into `harnesses/<harness-id>/` preserving all subdirectory structure. Use PowerShell:

```powershell
$src = "<local-source-path>"
$dst = "C:\Users\mailf\OneDrive\Documents\GitHub\harness-repository\harness-repository\harnesses\<harness-id>"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Get-ChildItem $src -Recurse | ForEach-Object {
  $rel = $_.FullName.Substring($src.Length).TrimStart('\')
  $target = Join-Path $dst $rel
  if ($_.PSIsContainer) {
    New-Item -ItemType Directory -Force -Path $target | Out-Null
  } else {
    $targetDir = Split-Path $target
    if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Force -Path $targetDir | Out-Null }
    Copy-Item $_.FullName -Destination $target -Force
  }
}
```

### 4 — Add attribution to the harness README

If a `README.md` exists in the harness folder, prepend an attribution block immediately after the first `#` heading:

```markdown
> **Attribution:** This harness is sourced from [owner/repo](https://github.com/owner/repo) by [@owner](https://github.com/owner), used under the [LICENSE] License. No modifications have been made to the original files.
```

Check the source repo's `LICENSE` file to fill in the license name. If no license is found, write "an open-source" instead.

If no `README.md` exists, create one with just the attribution block.

### 5 — Build the files list

Enumerate all files in `harnesses/<harness-id>/` recursively and build a `files[]` array for `harnesses.json`. For each file:

- `path`: `harnesses/<harness-id>/<relative-path-from-harness-root>` using forward slashes
- `type`: classify as follows:
  - `"documentation"` — `README.md`, `*.md` files at the harness root, `LICENSE`
  - `"config"` — `*.json`, `*.yaml`, `*.yml`, `*.toml` files, and files in a `rules/` subtree
  - `"template"` — everything else (scripts, skill files, hook scripts, etc.)
- `description`: derive a short description from the filename and parent directory (e.g. `"skills/dev-check/SKILL.md"` → `"dev-check skill"`)

Use PowerShell to enumerate:

```powershell
$base = "C:\Users\mailf\OneDrive\Documents\GitHub\harness-repository\harness-repository\harnesses\<harness-id>"
Get-ChildItem $base -Recurse -File | ForEach-Object {
  $rel = $_.FullName.Substring($base.Length + 1).Replace('\', '/')
  "harnesses/<harness-id>/$rel"
}
```

### 6 — Update harnesses.json

Read `harnesses.json`, append the new harness entry, and write it back. The entry shape:

```json
{
  "id": "<harness-id>",
  "name": "<human-readable name>",
  "description": "<one-sentence description>",
  "category": "<category>",
  "tags": ["<tag1>", "<tag2>"],
  "dependencies": [],
  "author": "<author> (<source-url>)",
  "version": "1.0.0",
  "files": [ ... ]
}
```

Also update `"lastUpdated"` to today's date in ISO 8601 format (`YYYY-MM-DDT00:00:00Z`).

Validate the JSON after writing:

```powershell
Get-Content "...harnesses.json" -Raw | ConvertFrom-Json | Select-Object -ExpandProperty harnesses | Select-Object id, name, @{N='files';E={$_.files.Count}}
```

### 7 — Confirm

Report to the user:
- Harness ID and name added
- Number of files registered
- Attribution line used
- Reminder to commit and push the harness-repository so the VS Code extension picks it up
