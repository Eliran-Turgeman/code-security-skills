---
name: security-scan
description: Run full code security scans (secrets, SAST, SCA, IaC) and render a unified report. Use for is my code secure, full scan, comprehensive security scan, or post-scan reporting.
---

## Goal

Run secrets, SAST, SCA, and IaC scans in parallel, normalize results to the canonical schema, and render a consistent report using the bundled script.

## Inputs

- Repo root mounted read-only at `/repo`
- Output directory mounted at `/out`

## Safety constraints

- Never print raw secrets.
- Only read from `/repo:ro`.
- Write outputs only to `/out`.
- Do not invent or drop fields in findings.

## Tool invocation (parallel)

Run all scanners in parallel, then wait for completion. Use the latest Docker image tags listed below.

### Bash (Linux/macOS)

```bash
mkdir -p out

# Gitleaks (directory scan; avoids "not a git repository" errors)
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:latest \
  dir /repo --report-path /out/gitleaks.json &

p1=$!

# Semgrep
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  semgrep/semgrep:latest \
  semgrep scan --config auto --json --json-output=/out/semgrep.json /repo &

p2=$!

# OSV-Scanner
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  ghcr.io/google/osv-scanner:latest \
  scan --format json --output /out/osv.json /repo &

p3=$!

# Trivy config
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  aquasec/trivy:latest \
  config --format json --output /out/trivy.json /repo &

p4=$!

wait $p1 $p2 $p3 $p4
```

### PowerShell (Windows)

```powershell
mkdir -Force out | Out-Null

$jobs = @()

$jobs += Start-Job { docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" zricethezav/gitleaks:latest dir /repo --report-path /out/gitleaks.json }
$jobs += Start-Job { docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" semgrep/semgrep:latest semgrep scan --config auto --json --json-output=/out/semgrep.json /repo }
$jobs += Start-Job { docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" ghcr.io/google/osv-scanner:latest scan --format json --output /out/osv.json /repo }
$jobs += Start-Job { docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" aquasec/trivy:latest config --format json --output /out/trivy.json /repo }

$jobs | Wait-Job | Receive-Job | Out-Null
$jobs | Remove-Job | Out-Null
```

Notes:

- If you want full git history scanning and your repo has `.git`, replace the Gitleaks command with `gitleaks git /repo --report-path /out/gitleaks.json`.

## Output normalization

Normalize each tool output into the canonical schema and write:

- `/out/findings.secrets.json` (from `/out/gitleaks.json`)
- `/out/findings.sast.json` (from `/out/semgrep.json`)
- `/out/findings.sca.json` (from `/out/osv.json`)
- `/out/findings.iac.json` (from `/out/trivy.json`)

Mapping rules:

### Secrets (Gitleaks)

- `category = secrets`
- `tool = gitleaks`
- `title` from rule description
- `file`, `start_line`, `end_line` from location
- `severity`: `critical` for high-confidence secrets, otherwise `high`
- `confidence`: from rule confidence if available, else `high`
- `evidence`: redacted snippet

### SAST (Semgrep)

- `category = sast`
- `tool = semgrep`
- `title` from rule message
- `file`, `start_line`, `end_line` from location
- `severity`: `ERROR` -> `high`, `WARNING` -> `medium`, `INFO` -> `low`
- `confidence`: from rule metadata if present, else `medium`
- `evidence`: short non-sensitive snippet

### SCA (OSV)

- `category = sca`
- `tool = osv`
- `title` from vulnerability summary or ID
- `package` and `version` from affected dependency
- `severity`: from OSV severity if present, else `medium`
- `confidence = high`
- `file`: manifest or lockfile if present, else `unknown`
- `start_line` and `end_line` set to `0` if not provided

### IaC (Trivy Config)

- `category = iac`
- `tool = trivy`
- `title` from check title
- `file`, `start_line`, `end_line` from location if available
- `severity` from Trivy severity
- `confidence = medium`
- `package` and `version` are null

## Reporting (mandatory)

After normalization, always run the reporting script to produce consistent output. Do not improvise reporting.

```bash
python skills/security-scan/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```

## Output

- `/out/report.json`: merged, triaged findings list
- `/out/report.md`: human-readable report in a consistent format

## How to rerun locally

Use the same Docker commands above, then run:

```bash
python skills/security-scan/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```

## Inline References

### Docker Images (Latest)

- gitleaks: `zricethezav/gitleaks:latest`
- semgrep: `semgrep/semgrep:latest`
- osv: `ghcr.io/google/osv-scanner:latest`
- trivy: `aquasec/trivy:latest`

Required runtime conventions:

- Mount repo read-only at `/repo:ro`
- Write outputs to `/out`
- No native installs

### Canonical Finding Schema

All skills must normalize tool output to this schema. Output is an array of findings in JSON.

#### Fields

- `id`: Stable hash derived from tool + file + location + rule id or fingerprint.
- `category`: `secrets` | `sast` | `sca` | `iac`
- `severity`: `critical` | `high` | `medium` | `low` | `info`
- `confidence`: `high` | `medium` | `low`
- `tool`: Scanner name (e.g., `gitleaks`, `semgrep`, `osv`, `trivy`)
- `title`: Short human-readable title
- `file`: Path relative to repo root
- `start_line`: 1-based line number
- `end_line`: 1-based line number
- `package`: Dependency name (SCA only; omit or null otherwise)
- `version`: Dependency version (SCA only; omit or null otherwise)
- `evidence`: Short snippet that avoids secrets; redact sensitive values
- `remediation`: Clear fix guidance

#### JSON Example

```json
[
  {
    "id": "sha256:5a8f...",
    "category": "secrets",
    "severity": "critical",
    "confidence": "high",
    "tool": "gitleaks",
    "title": "AWS access key detected",
    "file": "src/config.js",
    "start_line": 12,
    "end_line": 12,
    "package": null,
    "version": null,
    "evidence": "AWS_ACCESS_KEY_ID=REDACTED",
    "remediation": "Remove the secret, rotate the key, and use environment variables or a secrets manager."
  }
]
```

#### Normalization Rules

- Always include `id`, `category`, `severity`, `confidence`, `tool`, `title`, `file`.
- Use `null` for `package` and `version` when not applicable.
- Keep `evidence` to a short redacted snippet.
- Line numbers are required when the tool provides them; otherwise set to `0`.

### Triage Rules

These rules define prioritization across categories. All skills and the full scan must apply them when sorting findings.

#### Priority Order (Highest to Lowest)

1. Secrets (any severity)
2. RCE and injection issues (SAST)
3. SSRF and auth bypass (SAST)
4. Runtime dependency vulnerabilities (SCA)
5. Public IaC exposure or overly permissive access (IaC)
6. All other findings by severity

#### Severity Sort

Within each priority group, sort by severity:

`critical` > `high` > `medium` > `low` > `info`

#### Confidence Sort

Within same severity, sort by confidence:

`high` > `medium` > `low`

#### De-duplication

- Findings with the same `id` are considered duplicates.
- Prefer the finding with the higher severity or confidence.
