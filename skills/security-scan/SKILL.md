---
name: security-scan
description: Run full code security scans (secrets, SAST, SCA, IaC) and render a unified report. Use for is my code secure, full scan, comprehensive security scan, or post-scan reporting.
---

## Overview

Run a full security scan (secrets, SAST, SCA, IaC), normalize outputs deterministically, and render a consistent report. Do not use this skill for partial scans.

## Inputs

- Repository path (default: current directory)
- Output directory (default: `./out`)

## Outputs

- `out/gitleaks.json`
- `out/semgrep.json`
- `out/osv.json`
- `out/trivy.json`
- `out/findings.secrets.json`
- `out/findings.sast.json`
- `out/findings.sca.json`
- `out/findings.iac.json`
- `out/report.json`
- `out/report.md`

## Safety constraints

- Never print raw secrets.
- Only read from `/repo:ro`.
- Write outputs only to `/out`.
- Do not invent or drop fields in findings.
- Use the bundled scripts for normalization and reporting to ensure deterministic output.

## Steps (imperative)

1. Run all scanners sequentially. Use the exact per-tool commands below to run each scanner and produce raw JSON outputs in `out/`.
2. Ensure each tool completes successfully before starting the next.
2. Normalize findings with `normalize_findings.py` to produce `out/findings.*.json`.
3. Render the report with `render_report.py` to produce `out/report.json` and `out/report.md`.

## Quick start

Run each tool command sequentially, then normalize and report:

```bash
python skills/security-scan/scripts/normalize_findings.py --out-dir out
python skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

## Run scanners (per-tool commands)

Use the latest Docker image tags listed below. Run all four commands sequentially.

### Gitleaks (secrets)

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:latest \
  dir /repo --report-path /out/gitleaks.json
```

### Semgrep (SAST)

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  semgrep/semgrep:latest \
  semgrep scan --config auto --json --json-output=/out/semgrep.json /repo
```

### OSV-Scanner (SCA)

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  ghcr.io/google/osv-scanner:latest \
  scan --format json --output /out/osv.json /repo
```

### Trivy Config (IaC)

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  aquasec/trivy:latest \
  config --format json --output /out/trivy.json /repo
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
python skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

## Output

- `/out/report.json`: merged, triaged findings list
- `/out/report.md`: human-readable report in a consistent format

## Inline references

### Docker images (latest)

- gitleaks: `zricethezav/gitleaks:latest`
- semgrep: `semgrep/semgrep:latest`
- osv: `ghcr.io/google/osv-scanner:latest`
- trivy: `aquasec/trivy:latest`

Required runtime conventions:

- Mount repo read-only at `/repo:ro`
- Write outputs to `/out`
- No native installs

### Canonical finding schema

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

#### JSON example

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

#### Normalization rules

- Always include `id`, `category`, `severity`, `confidence`, `tool`, `title`, `file`.
- Use `null` for `package` and `version` when not applicable.
- Keep `evidence` to a short redacted snippet.
- Line numbers are required when the tool provides them; otherwise set to `0`.

### Triage rules

These rules define prioritization across categories. All skills and the full scan must apply them when sorting findings.

#### Priority order (highest to lowest)

1. Secrets (any severity)
2. RCE and injection issues (SAST)
3. SSRF and auth bypass (SAST)
4. Runtime dependency vulnerabilities (SCA)
5. Public IaC exposure or overly permissive access (IaC)
6. All other findings by severity

#### Severity sort

Within each priority group, sort by severity:

`critical` > `high` > `medium` > `low` > `info`

#### Confidence sort

Within same severity, sort by confidence:

`high` > `medium` > `low`

#### De-duplication

- Findings with the same `id` are considered duplicates.
- Prefer the finding with the higher severity or confidence.
