# scan-harnesses

Scan every skill and harness markdown file in this repository for harmful, malicious, or suspicious content before it can be loaded by the VS Code Harness Manager extension.

## Trigger

Use this skill when the user wants to audit harness or skill files for security issues. Phrases like "scan harnesses", "check for harmful content", "security scan skills", "audit harness files", or "run a safety check" should trigger it.

---

## Overview

Community-sourced harnesses are ingested from external GitHub repositories. A malicious contributor could embed:

- **Prompt injection** — instructions that hijack Claude's behaviour mid-session
- **Exfiltration payloads** — commands that read secrets, env vars, or SSH keys and send them outbound
- **Destructive commands** — `rm -rf`, format, or database-drop instructions
- **Social engineering** — urgency or authority language designed to bypass safety checks
- **Hidden instructions** — zero-width characters, HTML comments, or base64 blobs
- **Override / jailbreak patterns** — attempts to switch Claude into an unrestricted mode

This skill scans every `.md` file across `harnesses/` and `skills/` and reports any findings with file path, line number, severity, and a short explanation.

---

## Steps

### 1 — Locate the repository root and collect files

Detect the repository root automatically by finding the nearest ancestor directory that contains `harnesses.json`. This works regardless of where the repo is cloned.

```powershell
# Auto-detect repository root
function Get-HarnessRepoRoot {
    $dir = (Get-Location).Path
    while ($dir) {
        if (Test-Path (Join-Path $dir "harnesses.json")) { return $dir }
        $parent = Split-Path $dir -Parent
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    # Fallback: check if git can tell us
    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if ($gitRoot -and (Test-Path (Join-Path $gitRoot "harnesses.json"))) { return $gitRoot }
    } catch {}
    throw "Could not locate harness repository root. Run from within the harness-repository directory."
}

$root  = Get-HarnessRepoRoot
$files = Get-ChildItem "$root\harnesses", "$root\skills" -Recurse -Filter "*.md" -File
Write-Host "Repository root : $root"
Write-Host "Files to scan   : $($files.Count)"
```

---

### 2 — Run the detection scan

Run this PowerShell script. It checks every file against all detection categories and writes a structured findings list.

```powershell
function Get-HarnessRepoRoot {
    $dir = (Get-Location).Path
    while ($dir) {
        if (Test-Path (Join-Path $dir "harnesses.json")) { return $dir }
        $parent = Split-Path $dir -Parent
        if ($parent -eq $dir) { break }
        $dir = $parent
    }
    try {
        $gitRoot = git rev-parse --show-toplevel 2>$null
        if ($gitRoot -and (Test-Path (Join-Path $gitRoot "harnesses.json"))) { return $gitRoot }
    } catch {}
    throw "Could not locate harness repository root. Run from within the harness-repository directory."
}

$root  = Get-HarnessRepoRoot
$files = Get-ChildItem "$root\harnesses", "$root\skills" -Recurse -Filter "*.md" -File

# ── Detection rules ────────────────────────────────────────────────────────────
# Each rule: @{ Id; Severity; Category; Pattern (regex); Description }
$rules = @(

    # ── Prompt injection ──────────────────────────────────────────────────────
    @{ Id="PI-01"; Sev="CRITICAL"; Cat="Prompt Injection";
       Pat='ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|context)';
       Desc="Classic prompt injection — instructs the model to discard prior context." },

    @{ Id="PI-02"; Sev="CRITICAL"; Cat="Prompt Injection";
       Pat='disregard\s+(the\s+)?(above|previous|prior|all)\s*(instructions?|rules?)?';
       Desc="Instructs model to disregard established instructions." },

    @{ Id="PI-03"; Sev="HIGH"; Cat="Prompt Injection";
       Pat='new\s+instructions?\s*:';
       Desc="Attempts to inject a new instruction set mid-document." },

    @{ Id="PI-04"; Sev="HIGH"; Cat="Prompt Injection";
       Pat='(you\s+are\s+now|act\s+as|pretend\s+(you\s+are|to\s+be)|roleplay\s+as)\s+.{0,60}(unrestricted|jailbreak|no\s+limit|without\s+restriction|DAN|evil|hacked)';
       Desc="Attempts to redefine the model's identity as an unrestricted persona." },

    @{ Id="PI-05"; Sev="HIGH"; Cat="Prompt Injection";
       Pat='<\s*SYSTEM\s*>|<\s*/SYSTEM\s*>|\[SYSTEM\]|\[OVERRIDE\]|\[ADMIN\]';
       Desc="Fake system/admin tags used to elevate instruction authority." },

    @{ Id="PI-06"; Sev="HIGH"; Cat="Prompt Injection";
       Pat='(?i)(developer\s+mode|jailbreak\s+mode|unrestricted\s+mode|god\s+mode|no[\s-]filter\s+mode)';
       Desc="Attempts to activate a fictional unrestricted operating mode." },

    @{ Id="PI-07"; Sev="MEDIUM"; Cat="Prompt Injection";
       Pat='(?i)(override\s+safety|bypass\s+safeguard|disable\s+(safety|filter|guardrail)|circumvent\s+restriction)';
       Desc="Explicit instruction to disable model safety behaviour." },

    # ── Exfiltration ──────────────────────────────────────────────────────────
    @{ Id="EX-01"; Sev="CRITICAL"; Cat="Exfiltration";
       Pat='(curl|wget|Invoke-WebRequest|irm|iwr)\s+.*\$?(HOME|USERPROFILE|env:|AWS_|SECRET|API_KEY|TOKEN|PASSWORD|CREDENTIAL)';
       Desc="HTTP tool used alongside a sensitive environment variable — possible secret exfiltration." },

    @{ Id="EX-02"; Sev="CRITICAL"; Cat="Exfiltration";
       Pat='cat\s+~\/\.ssh\/|Get-Content.*\.ssh\\|type\s+.*\.ssh\\';
       Desc="Reads SSH private keys." },

    @{ Id="EX-03"; Sev="CRITICAL"; Cat="Exfiltration";
       Pat='cat\s+~\/\.aws\/credentials|Get-Content.*\.aws\\credentials|type\s+.*\.aws\\credentials';
       Desc="Reads AWS credentials file." },

    @{ Id="EX-04"; Sev="HIGH"; Cat="Exfiltration";
       Pat='\$env:(AWS_SECRET|AWS_ACCESS|GITHUB_TOKEN|ANTHROPIC_API_KEY|OPENAI_API_KEY|NPM_TOKEN|DOCKER_PASSWORD)';
       Desc="References a sensitive environment variable by name." },

    @{ Id="EX-05"; Sev="HIGH"; Cat="Exfiltration";
       Pat='(curl|wget|Invoke-WebRequest)\s+.*(-d|--data|body)\s+.*\$';
       Desc="Sends shell variable content to a remote URL — possible data exfiltration." },

    @{ Id="EX-06"; Sev="MEDIUM"; Cat="Exfiltration";
       Pat='(curl|wget)\s+https?://(?!github\.com|raw\.githubusercontent\.com|api\.github\.com|npmjs\.com|pypi\.org)[a-z0-9\-\.]+\.[a-z]{2,}.*\$\{?\w';
       Desc="Outbound HTTP call to an uncommon domain carrying a shell variable." },

    # ── Destructive commands ──────────────────────────────────────────────────
    @{ Id="DC-01"; Sev="CRITICAL"; Cat="Destructive Command";
       Pat='rm\s+-rf?\s+\/|rm\s+-rf?\s+~|Remove-Item\s+-Recurse\s+-Force\s+(C:\\|\/|~)';
       Desc="Deletes root, home, or entire drive recursively." },

    @{ Id="DC-02"; Sev="CRITICAL"; Cat="Destructive Command";
       Pat='(DROP\s+TABLE|DROP\s+DATABASE|TRUNCATE\s+TABLE)\s+\w';
       Desc="Destructive SQL statement." },

    @{ Id="DC-03"; Sev="HIGH"; Cat="Destructive Command";
       Pat='(format\s+[a-zA-Z]:|diskpart|del\s+\/[fFsS]\s+\/[sS]\s+\/[qQ]\s+[A-Za-z]:\\)';
       Desc="Windows disk-format or recursive forced-delete command." },

    @{ Id="DC-04"; Sev="HIGH"; Cat="Destructive Command";
       Pat='git\s+(push\s+.*--force|reset\s+--hard\s+HEAD~[5-9]|reset\s+--hard\s+HEAD~[0-9]{2,})';
       Desc="Potentially destructive git operation — force-push or large hard reset." },

    @{ Id="DC-05"; Sev="MEDIUM"; Cat="Destructive Command";
       Pat='(pkill|killall|taskkill)\s+(-9|-f|\/F)\s+\w';
       Desc="Forcefully terminates processes by name or signal." },

    # ── Hidden / obfuscated content ───────────────────────────────────────────
    @{ Id="HI-01"; Sev="HIGH"; Cat="Hidden Content";
       Pat='[​‌‍﻿­⁠]';
       Desc="Zero-width or invisible Unicode character — may conceal injected instructions." },

    @{ Id="HI-02"; Sev="HIGH"; Cat="Hidden Content";
       Pat='<!--[\s\S]{20,}-->';
       Desc="HTML comment with substantial content — possible hidden instruction block." },

    @{ Id="HI-03"; Sev="MEDIUM"; Cat="Hidden Content";
       Pat='(?i)[A-Za-z0-9+/]{60,}={0,2}(?![A-Za-z0-9+/=])';
       Desc="Long base64-like string — could be an obfuscated payload. Review manually." },

    @{ Id="HI-04"; Sev="MEDIUM"; Cat="Hidden Content";
       Pat='\\u00[0-9a-fA-F]{2}|\\x[0-9a-fA-F]{2}';
       Desc="Escape-encoded characters — may be used to bypass pattern matching." },

    # ── Social engineering ────────────────────────────────────────────────────
    @{ Id="SE-01"; Sev="HIGH"; Cat="Social Engineering";
       Pat='(?i)(this\s+is\s+a\s+(test|drill|simulation)|for\s+testing\s+purposes?\s+only)\s.{0,80}(skip|bypass|ignore|disable)';
       Desc="Claims this is a test/drill to justify bypassing normal behaviour." },

    @{ Id="SE-02"; Sev="HIGH"; Cat="Social Engineering";
       Pat='(?i)(urgent|immediately|right\s+now|without\s+delay).{0,60}(execute|run|delete|send|exfil|bypass)';
       Desc="Urgency language paired with a sensitive action — social engineering pattern." },

    @{ Id="SE-03"; Sev="MEDIUM"; Cat="Social Engineering";
       Pat='(?i)(anthropic\s+engineer|openai\s+staff|system\s+administrator|authorized\s+override)\s+(says?|here|confirms?|approves?)';
       Desc="Impersonates a trusted authority to grant elevated permissions." },

    @{ Id="SE-04"; Sev="MEDIUM"; Cat="Social Engineering";
       Pat='(?i)do\s+not\s+(tell|inform|mention|show|reveal)\s+(the\s+)?(user|human|operator)';
       Desc="Instructs the model to hide its actions from the user." },

    # ── Override / jailbreak markers ─────────────────────────────────────────
    @{ Id="OV-01"; Sev="CRITICAL"; Cat="Override";
       Pat='(?i)(DAN|Do\s+Anything\s+Now|STAN|DUDE|AIM|ANTI-DAN)\b';
       Desc="Known jailbreak persona name detected." },

    @{ Id="OV-02"; Sev="HIGH"; Cat="Override";
       Pat='(?i)(enable\s+)?(unrestricted|unfiltered|uncensored)\s+(mode|output|response|access)';
       Desc="Attempts to switch model into an unfiltered output mode." },

    @{ Id="OV-03"; Sev="HIGH"; Cat="Override";
       Pat='(?i)respond\s+(only\s+)?(in\s+)?raw\s+(json|yaml|text)\s+without\s+(any\s+)?(safety|filter|restriction|guardrail)';
       Desc="Instructs model to produce unguarded output by framing it as a formatting requirement." },

    # ── Suspicious network / install patterns ─────────────────────────────────
    @{ Id="NW-01"; Sev="HIGH"; Cat="Suspicious Network";
       Pat='(curl|wget|Invoke-WebRequest)\s+.*\|\s*(bash|sh|pwsh|powershell|python|node|ruby)';
       Desc="Pipe-to-shell pattern — downloads and immediately executes remote code." },

    @{ Id="NW-02"; Sev="MEDIUM"; Cat="Suspicious Network";
       Pat='(npm|pip|cargo|gem)\s+install\s+.*--script\s+https?://';
       Desc="Package install with a remote post-install script URL." }
)

# ── Scan ───────────────────────────────────────────────────────────────────────
$findings = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($file in $files) {
    $relPath = $file.FullName.Substring($root.Length + 1).Replace('\', '/')
    $lines   = Get-Content $file.FullName -Encoding utf8 -ErrorAction SilentlyContinue
    if (-not $lines) { continue }

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        foreach ($rule in $rules) {
            if ($line -match $rule.Pat) {
                $findings.Add([PSCustomObject]@{
                    Severity = $rule.Sev
                    Id       = $rule.Id
                    Category = $rule.Cat
                    File     = $relPath
                    Line     = $i + 1
                    Content  = $line.Trim().Substring(0, [Math]::Min(120, $line.Trim().Length))
                    Desc     = $rule.Desc
                })
            }
        }
    }
}

# ── Report ────────────────────────────────────────────────────────────────────
$order = @{ CRITICAL=0; HIGH=1; MEDIUM=2; LOW=3 }
$sorted = $findings | Sort-Object { $order[$_.Severity] }, File, Line

if ($sorted.Count -eq 0) {
    Write-Host "`n✅  No harmful content detected across $($files.Count) files." -ForegroundColor Green
} else {
    $critCount = ($sorted | Where-Object Severity -eq 'CRITICAL').Count
    $highCount = ($sorted | Where-Object Severity -eq 'HIGH').Count
    $medCount  = ($sorted | Where-Object Severity -eq 'MEDIUM').Count

    Write-Host "`n⚠️  Scan complete — $($sorted.Count) finding(s) across $($files.Count) files" -ForegroundColor Yellow
    Write-Host "   CRITICAL: $critCount   HIGH: $highCount   MEDIUM: $medCount`n" -ForegroundColor Yellow

    foreach ($f in $sorted) {
        $colour = switch ($f.Severity) { 'CRITICAL' { 'Red' } 'HIGH' { 'DarkYellow' } default { 'Cyan' } }
        Write-Host "[$($f.Severity)] $($f.Id) — $($f.Category)" -ForegroundColor $colour
        Write-Host "  File : $($f.File):$($f.Line)"
        Write-Host "  Rule : $($f.Desc)"
        Write-Host "  Line : $($f.Content)"
        Write-Host ""
    }
}

# Return structured results for further processing
$sorted
```

---

### 3 — Triage each finding

For every finding, manually inspect the file and line referenced:

1. **Open the file** at the reported line number.
2. **Determine intent** — is this a legitimate code example demonstrating a dangerous command (e.g., a skill explaining how to avoid `rm -rf`), or is it an actual harmful instruction embedded in the skill?
3. **Classify**:
   - **False positive** — document why and suppress (see Step 4).
   - **Genuine threat** — remove the harness or quarantine the file (see Step 5).

---

### 4 — Suppress false positives

If a finding is a false positive (e.g., a SKILL.md legitimately warns users *about* a dangerous command pattern), add a suppression comment on the same line:

```markdown
<!-- scan-suppress: DC-01 reason: this is a documented anti-pattern, not an instruction -->
```

On the next scan run, lines containing `scan-suppress: <ID>` are skipped for that rule.

To apply suppression awareness, add this filter inside the scan loop (after the `$line` assignment):

```powershell
# Skip suppressed lines
if ($line -match "scan-suppress:\s*$($rule.Id)") { continue }
```

---

### 5 — Handle genuine threats

If a finding is confirmed malicious:

1. **Quarantine the harness** — remove its folder from `harnesses/` and its entry from `harnesses.json`:

```powershell
$root    = Get-HarnessRepoRoot   # defined above
$harness = "<harness-id>"

Remove-Item (Join-Path $root "harnesses\$harness") -Recurse -Force

$repoJson = Join-Path $root "harnesses.json"
$json = Get-Content $repoJson -Raw | ConvertFrom-Json
$json.harnesses = $json.harnesses | Where-Object { $_.id -ne $harness }
$json | ConvertTo-Json -Depth 20 | Set-Content $repoJson -Encoding utf8
Write-Host "Harness '$harness' removed."
```

2. **Commit the removal** and note the security reason in the commit message.
3. **Report upstream** — open an issue on the source repository so the original author is aware.

---

### 6 — Confirm and report

After triage, report back to the user:

- Total files scanned
- Findings by severity (CRITICAL / HIGH / MEDIUM)
- Actions taken (suppressions added, harnesses removed)
- Recommendation: run this skill again after every new `import-harness` operation
