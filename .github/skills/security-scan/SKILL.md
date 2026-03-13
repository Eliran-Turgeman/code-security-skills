---
name: security-scan
description: 'Run a full security scan (secrets + SAST + SCA + IaC) using Dockerized scanners (Gitleaks, Semgrep, OSV-Scanner, Trivy), then normalize and render a unified report. Use for: "is my code secure", comprehensive security scan, code scan, secrets scan, SAST scan, supply-chain scan, IaC scan, or generating report.md/report.json for CI artifacts. Never use for partial scans.'
argument-hint: 'Run from the repo root; outputs written to ./out.'
---

# Security Scan (Full)

This skill runs **all four** categories of scanners and produces a **single, consistent report** for builders who don’t have a security background.

## What You Get

The scan writes raw tool outputs plus normalized findings and a rendered report.

- Raw scanner outputs (JSON): `out/gitleaks.json`, `out/semgrep.json`, `out/osv.json`, `out/trivy.json`
- Normalized findings (canonical schema): `out/findings.secrets.json`, `out/findings.sast.json`, `out/findings.sca.json`, `out/findings.iac.json`
- Unified report: `out/report.json`, `out/report.md`

## Safety Rules (Non-Negotiable)

- Never print or paste raw secrets (including scan outputs) into chat, issues, or logs.
- Scanners must read the repo **read-only** (`/repo:ro`) and write outputs only to `/out`.
- Normalization/reporting must use the bundled scripts:
  - [normalize_findings.py](./scripts/normalize_findings.py)
  - [render_report.py](./scripts/render_report.py)
- Do not change the finding schema or drop fields.
- Treat `out/` as sensitive: don’t commit it and don’t upload it to public locations.

## What This Scan Does NOT Cover (Avoid False Confidence)

This skill is a strong **static** baseline, but it does not replace:

- **DAST** (testing a running service via HTTP)
- **Container image vulnerability scanning** (unless you separately build + scan an image)
- **Cloud/runtime posture** (IAM, network exposure, key vault policies) unless captured in IaC in-repo
- **Business-logic flaws** and threat-model-specific issues

## Prerequisites

- Docker is installed and running.
- You have permission to run containers.
- You run commands from the **repo root**.

## Procedure (Stop if Any Step Fails)

### 0) Prepare Output Folder

PowerShell (Windows):

```powershell
New-Item -ItemType Directory -Force out | Out-Null
$repo = (Get-Location).Path
$out  = Join-Path $repo 'out'
```

Bash (macOS/Linux/Git Bash):

```bash
mkdir -p out
```

### 1) Run Scanners (Dockerized)

Run these **sequentially**. Do not proceed to normalization until all four JSON files exist.

#### 1A) Gitleaks (Secrets)

PowerShell:

```powershell
docker run --rm -v "${repo}:/repo:ro" -v "${out}:/out" zricethezav/gitleaks:latest detect --source /repo --report-format json --report-path /out/gitleaks.json --redact
```

Bash:

```bash
docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" zricethezav/gitleaks:latest detect --source /repo --report-format json --report-path /out/gitleaks.json --redact
```

Optional (full git history scanning, if `.git` exists):

```text
gitleaks detect --source /repo --report-format json --report-path /out/gitleaks.json --redact --log-opts="--all"
```

#### 1B) Semgrep (SAST)

PowerShell:

```powershell
docker run --rm -e SEMGREP_SEND_METRICS=off -v "${repo}:/repo:ro" -v "${out}:/out" semgrep/semgrep:latest semgrep scan --config auto --json --json-output=/out/semgrep.json /repo
```

Bash:

```bash
docker run --rm -e SEMGREP_SEND_METRICS=off -v "$PWD:/repo:ro" -v "$PWD/out:/out" semgrep/semgrep:latest semgrep scan --config auto --json --json-output=/out/semgrep.json /repo
```

#### 1C) OSV-Scanner (SCA / Dependencies)

PowerShell:

```powershell
docker run --rm -v "${repo}:/repo:ro" -v "${out}:/out" ghcr.io/google/osv-scanner:latest scan --format json --output /out/osv.json /repo
```

Bash:

```bash
docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" ghcr.io/google/osv-scanner:latest scan --format json --output /out/osv.json /repo
```

#### 1D) Trivy Config (IaC / Misconfigurations)

PowerShell:

```powershell
docker run --rm -v "${repo}:/repo:ro" -v "${out}:/out" aquasec/trivy:latest config --format json --output /out/trivy.json /repo
```

Bash:

```bash
docker run --rm -v "$PWD:/repo:ro" -v "$PWD/out:/out" aquasec/trivy:latest config --format json --output /out/trivy.json /repo
```

### 2) Normalize to Canonical Findings

This produces `out/findings.*.json` using the canonical schema.

Option A (local Python 3):

```bash
python .github/skills/security-scan/scripts/normalize_findings.py --out-dir out
```

Option B (no local Python; run via Docker):

PowerShell:

```powershell
docker run --rm -v "${repo}:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/normalize_findings.py --out-dir out
```

Bash:

```bash
docker run --rm -v "$PWD:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/normalize_findings.py --out-dir out
```

### 3) Render a Unified Report (Mandatory)

Option A (local Python 3):

```bash
python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

Option B (Dockerized Python):

PowerShell:

```powershell
docker run --rm -v "${repo}:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

Bash:

```bash
docker run --rm -v "$PWD:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

### 4) Completion Checks

Confirm these files exist:

- `out/gitleaks.json`
- `out/semgrep.json`
- `out/osv.json`
- `out/trivy.json`
- `out/report.md`

If any raw scanner JSON is missing, treat the scan as **incomplete coverage** and rerun the missing scanner(s) (do not ship based on partial results).

### 5) Artifact Handling (Recommended)

Raw scanner outputs can contain sensitive information (especially `semgrep.json`, and sometimes `gitleaks.json` depending on tool behavior/version).

- Keep `out/` private.
- In CI, store artifacts only in secured storage with retention limits.
- After you’ve produced `out/report.md` (and optionally `out/report.json`), consider deleting the raw scanner outputs:

PowerShell:

```powershell
Remove-Item -Force out\gitleaks.json,out\semgrep.json,out\osv.json,out\trivy.json -ErrorAction SilentlyContinue
```

## How to Consume Results (For Inexperienced Engineers)

- Start with `out/report.md` → **Top 10 Fixes**.
- Fix **secrets first**: remove, rotate, and prevent re-introduction (environment variables + secrets manager).
- Then fix **high severity SAST** issues that mention injection/RCE/auth bypass.
- Then fix dependency vulnerabilities by upgrading packages.
- Then fix IaC findings that mention public exposure or overly permissive access.

## Tool Versions (Stability Note)

This workflow is deterministic given the tool outputs, but using Docker `:latest` means scanners can change over time. If you need reproducible CI, pin image tags or digests for all four scanners.

### Pinning Docker Images (Recommended for CI)

Replace `:latest` with a version tag or digest. Example patterns:

- Tag: `semgrep/semgrep:1.XX.YY`
- Digest: `semgrep/semgrep@sha256:<digest>`

One simple approach is to define environment variables and use them in the commands:

PowerShell:

```powershell
$GITLEAKS_IMAGE = 'zricethezav/gitleaks:<tag-or-digest>'
$SEMGREP_IMAGE  = 'semgrep/semgrep:<tag-or-digest>'
$OSV_IMAGE      = 'ghcr.io/google/osv-scanner:<tag-or-digest>'
$TRIVY_IMAGE    = 'aquasec/trivy:<tag-or-digest>'
```

Then replace the image names in the `docker run` commands.

## CI Mode (Recommended)

### Gate on severity

Fail the job if any finding is at or above a severity threshold:

```bash
python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md --fail-on high
```

### Gate on secrets only

Fail if any secrets are found (regardless of severity):

```bash
python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md --fail-on info --fail-on-category secrets
```

## Troubleshooting (Common)

- **Docker mount errors (Windows)**: ensure Docker Desktop is running and the drive is shared/allowed for file sharing.
- **Path with spaces**: keep the PowerShell commands exactly as written (quoted `-v "${repo}:/repo:ro"`).
- **Empty report**: confirm all four raw JSON files exist in `out/` before normalization.
- **Git Bash on Windows**: prefer PowerShell. If you must use Git Bash, you may need to disable path conversion for volume mounts (e.g., set `MSYS_NO_PATHCONV=1`).
