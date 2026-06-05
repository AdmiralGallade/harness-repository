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

If the source is a GitHub URL, use the **Import from GitHub URL** function below to clone it automatically into a temporary directory — do not ask the user to clone it manually.

### 1b — Import from GitHub URL

When the source is a GitHub URL, run this function to shallow-clone the repo into a temporary directory and return the local path for use in subsequent steps.

```powershell
function Import-HarnessFromGitHub {
    param(
        [Parameter(Mandatory)][string]$GitHubUrl  # e.g. https://github.com/owner/repo
    )

    # Derive a safe folder name from the URL
    $repoSlug = ($GitHubUrl.TrimEnd('/') -split '/')[-1]   # last path segment
    $tmpDir   = Join-Path $env:TEMP "harness-import-$repoSlug"

    # Remove any stale clone
    if (Test-Path $tmpDir) {
        Remove-Item $tmpDir -Recurse -Force
    }

    Write-Host "Cloning $GitHubUrl into $tmpDir ..."
    git clone --depth 1 $GitHubUrl $tmpDir

    if (-not $?) {
        throw "git clone failed for $GitHubUrl. Check the URL and your network connection."
    }

    # Remove the .git folder — we only want the source files
    $gitDir = Join-Path $tmpDir ".git"
    if (Test-Path $gitDir) {
        Remove-Item $gitDir -Recurse -Force
    }

    Write-Host "Cloned successfully. Source path: $tmpDir"
    return $tmpDir
}

# Usage — call before Step 3:
# $sourcePath = Import-HarnessFromGitHub -GitHubUrl "https://github.com/owner/repo"
```

After Step 3 (copying files), clean up the temporary clone:

```powershell
# Cleanup — run after the copy in Step 3 is complete
$repoSlug = ($GitHubUrl.TrimEnd('/') -split '/')[-1]
$tmpDir   = Join-Path $env:TEMP "harness-import-$repoSlug"
if (Test-Path $tmpDir) {
    Remove-Item $tmpDir -Recurse -Force
    Write-Host "Temporary clone removed."
}
```

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

### 7 — Security scan

After registering the harness, automatically run the security scanner across all `.md` files in the new harness folder. This catches harmful content before it is committed.

```powershell
$root      = "C:\Users\mailf\OneDrive\Documents\GitHub\harness-repository\harness-repository"
$harnessId = "<harness-id>"   # replace with the actual id
$scanRoot  = "$root\harnesses\$harnessId"

$files = Get-ChildItem $scanRoot -Recurse -Filter "*.md" -File
Write-Host "`nRunning security scan on $($files.Count) files in harnesses/$harnessId ...`n"

$rules = @(
    @{ Id="PI-01"; Sev="CRITICAL"; Cat="Prompt Injection";    Pat='ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|context)' },
    @{ Id="PI-02"; Sev="CRITICAL"; Cat="Prompt Injection";    Pat='disregard\s+(the\s+)?(above|previous|prior|all)\s*(instructions?|rules?)?' },
    @{ Id="PI-03"; Sev="HIGH";     Cat="Prompt Injection";    Pat='new\s+instructions?\s*:' },
    @{ Id="PI-04"; Sev="HIGH";     Cat="Prompt Injection";    Pat='(you\s+are\s+now|act\s+as|pretend\s+(you\s+are|to\s+be)|roleplay\s+as)\s+.{0,60}(unrestricted|jailbreak|no\s+limit|DAN|evil|hacked)' },
    @{ Id="PI-05"; Sev="HIGH";     Cat="Prompt Injection";    Pat='<\s*SYSTEM\s*>|<\s*/SYSTEM\s*>|\[SYSTEM\]|\[OVERRIDE\]|\[ADMIN\]' },
    @{ Id="PI-06"; Sev="HIGH";     Cat="Prompt Injection";    Pat='(?i)(developer\s+mode|jailbreak\s+mode|unrestricted\s+mode|god\s+mode|no[\s-]filter\s+mode)' },
    @{ Id="PI-07"; Sev="MEDIUM";   Cat="Prompt Injection";    Pat='(?i)(override\s+safety|bypass\s+safeguard|disable\s+(safety|filter|guardrail)|circumvent\s+restriction)' },
    @{ Id="EX-01"; Sev="CRITICAL"; Cat="Exfiltration";        Pat='(curl|wget|Invoke-WebRequest|irm|iwr)\s+.*\$?(HOME|USERPROFILE|env:|AWS_|SECRET|API_KEY|TOKEN|PASSWORD|CREDENTIAL)' },
    @{ Id="EX-02"; Sev="CRITICAL"; Cat="Exfiltration";        Pat='cat\s+~\/\.ssh\/|Get-Content.*\.ssh\\|type\s+.*\.ssh\\' },
    @{ Id="EX-03"; Sev="CRITICAL"; Cat="Exfiltration";        Pat='cat\s+~\/\.aws\/credentials|Get-Content.*\.aws\\credentials' },
    @{ Id="EX-04"; Sev="HIGH";     Cat="Exfiltration";        Pat='\$env:(AWS_SECRET|AWS_ACCESS|GITHUB_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY|NPM_TOKEN|DOCKER_PASSWORD)' },
    @{ Id="EX-05"; Sev="HIGH";     Cat="Exfiltration";        Pat='(curl|wget|Invoke-WebRequest)\s+.*(-d|--data|body)\s+.*\$' },
    @{ Id="DC-01"; Sev="CRITICAL"; Cat="Destructive Command"; Pat='rm\s+-rf?\s+\/|rm\s+-rf?\s+~|Remove-Item\s+-Recurse\s+-Force\s+(C:\\|\/|~)' },
    @{ Id="DC-02"; Sev="CRITICAL"; Cat="Destructive Command"; Pat='(DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE\s+TABLE)\s+\w' },
    @{ Id="DC-03"; Sev="HIGH";     Cat="Destructive Command"; Pat='(format\s+[a-zA-Z]:|diskpart|del\s+\/[fFsS]\s+\/[sS]\s+\/[qQ]\s+[A-Za-z]:\\)' },
    @{ Id="DC-04"; Sev="HIGH";     Cat="Destructive Command"; Pat='git\s+(push\s+.*--force|reset\s+--hard\s+HEAD~[5-9]|reset\s+--hard\s+HEAD~[0-9]{2,})' },
    @{ Id="HI-01"; Sev="HIGH";     Cat="Hidden Content";      Pat='[​‌‍﻿­⁠]' },
    @{ Id="HI-02"; Sev="HIGH";     Cat="Hidden Content";      Pat='<!--.{20,}-->' },
    @{ Id="HI-03"; Sev="MEDIUM";   Cat="Hidden Content";      Pat='(?i)[A-Za-z0-9+/]{60,}={0,2}(?![A-Za-z0-9+/=])' },
    @{ Id="SE-01"; Sev="HIGH";     Cat="Social Engineering";  Pat='(?i)(this\s+is\s+a\s+(test|drill|simulation)).{0,80}(skip|bypass|ignore|disable)' },
    @{ Id="SE-02"; Sev="HIGH";     Cat="Social Engineering";  Pat='(?i)(urgent|immediately|right\s+now).{0,60}(execute|run|delete|send|bypass)' },
    @{ Id="SE-04"; Sev="MEDIUM";   Cat="Social Engineering";  Pat='(?i)do\s+not\s+(tell|inform|mention|show|reveal)\s+(the\s+)?(user|human|operator)' },
    @{ Id="OV-01"; Sev="CRITICAL"; Cat="Override";            Pat='(?i)\b(DAN|Do\s+Anything\s+Now|STAN|DUDE|ANTI-DAN)\b' },
    @{ Id="OV-02"; Sev="HIGH";     Cat="Override";            Pat='(?i)(enable\s+)?(unrestricted|unfiltered|uncensored)\s+(mode|output|response|access)' },
    @{ Id="NW-01"; Sev="HIGH";     Cat="Suspicious Network";  Pat='(curl|wget|Invoke-WebRequest)\s+.*\|\s*(bash|sh|pwsh|powershell|python|node|ruby)' }
)

$findings = [System.Collections.Generic.List[PSCustomObject]]::new()
foreach ($file in $files) {
    $relPath = $file.FullName.Substring($root.Length+1).Replace('\','/')
    $lines   = Get-Content $file.FullName -Encoding utf8 -ErrorAction SilentlyContinue
    if (-not $lines) { continue }
    for ($i=0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        if ($line -match 'scan-suppress') { continue }
        foreach ($rule in $rules) {
            if ($line -match $rule.Pat) {
                $findings.Add([PSCustomObject]@{
                    Severity=$rule.Sev; Id=$rule.Id; Category=$rule.Cat
                    File=$relPath; Line=($i+1)
                    Content=$line.Trim().Substring(0,[Math]::Min(120,$line.Trim().Length))
                })
            }
        }
    }
}

# ── Print report ──────────────────────────────────────────────────────────────
$order  = @{ CRITICAL=0; HIGH=1; MEDIUM=2; LOW=3 }
$sorted = $findings | Sort-Object { $order[$_.Severity] }, File, Line

$reportPath = "$root\harnesses\$harnessId\SCAN-REPORT.md"
$lines = @()
$lines += "# Security Scan Report — $harnessId"
$lines += ""
$lines += "Scanned: $(Get-Date -Format 'yyyy-MM-dd HH:mm')  |  Files: $($files.Count)  |  Findings: $($sorted.Count)"
$lines += ""

if ($sorted.Count -eq 0) {
    Write-Host "✅  No harmful content detected across $($files.Count) files." -ForegroundColor Green
    $lines += "## ✅ Clean"
    $lines += ""
    $lines += "No harmful content detected."
} else {
    $c = ($sorted|Where-Object Severity -eq 'CRITICAL').Count
    $h = ($sorted|Where-Object Severity -eq 'HIGH').Count
    $m = ($sorted|Where-Object Severity -eq 'MEDIUM').Count
    Write-Host "⚠️  $($sorted.Count) finding(s) — CRITICAL:$c  HIGH:$h  MEDIUM:$m" -ForegroundColor Yellow
    $lines += "## ⚠️ Findings"
    $lines += ""
    $lines += "| Severity | Rule | Category | File | Line | Content |"
    $lines += "|----------|------|----------|------|------|---------|"
    foreach ($f in $sorted) {
        $escaped = $f.Content -replace '\|', '\|'
        $lines += "| $($f.Severity) | $($f.Id) | $($f.Category) | ``$($f.File)`` | $($f.Line) | $escaped |"
        Write-Host "[$($f.Severity)] $($f.Id) | $($f.File):$($f.Line)" -ForegroundColor $(if($f.Severity -eq 'CRITICAL'){'Red'}elseif($f.Severity -eq 'HIGH'){'DarkYellow'}else{'Cyan'})
        Write-Host "  $($f.Content)"
    }
    $lines += ""
    $lines += "## Next steps"
    $lines += ""
    $lines += "- Review each finding and determine if it is a genuine issue or a false positive."
    $lines += "- For false positives, add ``<!-- scan-suppress: <ID> reason: ... -->`` on the flagged line."
    $lines += "- For genuine threats, remove the harness or quarantine the file (see ``skills/scan-harnesses/SKILL.md`` Step 5)."
}

$lines | Set-Content $reportPath -Encoding utf8
Write-Host "`nReport written to: harnesses/$harnessId/SCAN-REPORT.md"
```

The report is saved as `harnesses/<harness-id>/SCAN-REPORT.md` inside the harness folder. It is a markdown file with a severity table, file paths, line numbers, and matched content.

If **any CRITICAL findings** are present, **stop and do not commit**. Present the findings to the user and ask how to proceed before running Step 8.

### 8 — Confirm

Report to the user:
- Harness ID and name added
- Number of files registered
- Attribution line used
- Security scan summary (files scanned, finding counts by severity)
- Location of the full report: `harnesses/<harness-id>/SCAN-REPORT.md`
- Reminder to commit and push the harness-repository so the VS Code extension picks it up
