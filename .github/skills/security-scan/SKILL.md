---
name: security-scan
description: 'Run a full security scan (secrets + SAST + SCA + IaC) using Dockerized scanners (Gitleaks, Semgrep, OSV-Scanner, Trivy), then normalize/render a unified report and run LAUNCH_SECURITY_CHECK for behavioral and architecture flaws static scanners may miss. Use for: "is my code secure", comprehensive security scan, code scan, secrets scan, SAST scan, supply-chain scan, IaC scan, or generating report.md/report.json for CI artifacts. Never use for partial scans.'
argument-hint: 'Run from the repo root; outputs written to ./out.'
---

# Security Scan (Full)

This skill runs **all four** categories of scanners and produces a **single, consistent report** for builders who don’t have a security background.

After static results are generated, run a **LAUNCH_SECURITY_CHECK** manual review for high-impact issues that scanners often miss.

## What You Get

The scan writes raw tool outputs plus normalized findings, an agent-curated finding set, and a rendered report.

- Raw scanner outputs (JSON): `out/gitleaks.json`, `out/semgrep.json`, `out/osv.json`, `out/trivy.json`
- Normalized findings (canonical schema): `out/findings.secrets.json`, `out/findings.sast.json`, `out/findings.sca.json`, `out/findings.iac.json`
- Agent-curated findings (prioritized, de-noised, combo-aware): `out/findings.agent.json`
- Unified report: `out/report.json`, `out/report.md`
- Manual review findings (recommended): `out/manual-review.md`

## Safety Rules (Non-Negotiable)

- Never print or paste raw secrets (including scan outputs) into chat, issues, or logs.
- Scanners must read the repo **read-only** (`/repo:ro`) and write outputs only to `/out`.
- Normalization/reporting must use the bundled scripts:
  - [normalize_findings.py](./scripts/normalize_findings.py)
  - [render_report.py](./scripts/render_report.py)
- Do not change the canonical finding schema or drop fields. If you add fields (e.g., `triage`, `triage_reason`), keep all original fields intact.
- Treat `out/` as sensitive: don’t commit it and don’t upload it to public locations.

## What This Scan Does NOT Cover (Avoid False Confidence)

This skill is a strong **static** baseline, but it does not replace:

- **DAST** (testing a running service via HTTP)
- **Container image vulnerability scanning** (unless you separately build + scan an image)
- **Cloud/runtime posture** (IAM, network exposure, key vault policies) unless captured in IaC in-repo
- **Business-logic flaws** and threat-model-specific issues

## LAUNCH_SECURITY_CHECK (Mandatory Manual Review)

When performing a `LAUNCH_SECURITY_CHECK`, analyze the repository and attempt to detect security issues that static scanners commonly miss.

Focus on architectural and behavioral mistakes that often lead to real-world breaches. Prioritize findings that could realistically cause account takeover, data leaks, or infrastructure compromise if deployed today.

Attempt to detect the following patterns:

1. Missing rate limiting on sensitive endpoints (`/login`, `/signup`, password reset, OTP, verification flows)
2. Admin or internal routes exposed without authentication (`/admin`, `/internal`, `/debug`, `/metrics`, `/test`)
3. File upload handling without validation (type allowlist, size limits, filename/path sanitization)
4. Path traversal risk (user-controlled input used in file paths without sanitization)
5. Dangerous logging of secrets or credentials (tokens, passwords, auth headers, cookies, API keys, env vars)
6. Debug/development configuration enabled in deployable paths (debug flags, verbose errors, dev servers)
7. Hardcoded authentication secrets (JWT/session/encryption/OAuth secrets in code or config)
8. Weak JWT usage (no expiration, insecure algorithm, incomplete signature/claims validation)
9. Missing authorization checks (resource access endpoints lacking ownership/permission verification)
10. Unsafe user input usage (raw input flowing into queries, commands, templates, or filesystem operations)
11. Dangerous CORS configuration (`*`, unrestricted origins, unsafe credentialed cross-origin access)
12. Sensitive files committed (`.env`, dumps, key files, credential JSON, backups)
13. Missing security headers (CSP, X-Frame-Options, HSTS, X-Content-Type-Options)
14. Public cloud credentials or service keys (AWS keys, Firebase, Supabase service role keys, similar tokens)
15. Authentication flows relying on client-side trust (client-provided role/user/permission values trusted server-side)

For each issue found, provide:

- `severity`
- `evidence` (file path and a minimal snippet or line reference)
- `why this is dangerous`
- `recommended fix`

If no credible issue is found for a pattern, state that explicitly and avoid speculative claims.

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

### 3) Agent Triage (Toxic Combinations + Codebase Context)

This step is **agent-driven** (not a script).

Goal: starting from the normalized findings (`out/findings.*.json`), produce `out/findings.agent.json` that is:

- **Prioritized using toxic combinations** (defined below; not user-supplied config)
- **Contextualized using the actual codebase** (paths, call sites, whether reachable in production)
- **Actionable** (clear `triage_reason` and remediation guidance)

Rules for what the agent may change:

- **Suppress** obvious false positives (keep the record but set `triage: suppressed` and explain why)
- **Merge/deduplicate** duplicates across tools into one best record (keep the strongest evidence and add `also_found_by` if helpful)
- **Escalate or de-escalate** severity/confidence/triage tier based on code context
- **Add derived findings** (e.g., a composite “toxic combo” finding) when multiple independent findings combine into a higher-risk scenario
- **Delete** only if the finding is malformed/unusable (missing file/package and no usable evidence); otherwise prefer `suppressed` for auditability

Safety constraints for this step:

- Never paste raw secrets. Never include token-like strings in `evidence`.
- If quoting code for context, keep it minimal and redact any token-like values. Prefer referencing file paths + function names over copying code.

#### Toxic Combinations (Agent-Defined)

Treat these combinations as **higher risk than the individual findings**. When a combo matches, do both:

1) Escalate involved findings to `triage: action_required` (unless they are clearly test/demo/vendor)
2) Add one composite finding with `category: toxic_combo` summarizing the combined risk

Combos:

- **Leaked secret + public exposure**
  - Signals: any `secrets` finding + any IaC finding indicating public exposure (`public`, `0.0.0.0/0`, “open to the internet”, unrestricted ingress)
  - Why higher risk: credentials + exposure increases immediate exploitability and blast radius
- **RCE/injection + inbound exposure**
  - Signals: SAST indicating command injection / SQLi / SSTI / deserialization + an internet-facing route/service or public ingress
  - Why higher risk: reachable exploitation path
- **SSRF + cloud metadata / credential access**
  - Signals: SSRF-like finding + evidence of requests to metadata endpoints (e.g., `169.254.169.254`) or default credentials chains
  - Why higher risk: credential theft leading to infra compromise
- **High-severity dependency vuln + runtime usage**
  - Signals: SCA high/critical + dependency appears in runtime codepaths (not test/dev-only)
  - Why higher risk: practical exploitability
- **Public data store + weak/no auth**
  - Signals: IaC public database/storage exposure + app lacks authentication/authorization on relevant endpoints
  - Why higher risk: direct data exfiltration risk

#### Context Enrichment (Agent-Driven)

For each action-required/review finding:

- Confirm whether the file is **production code** vs **tests/examples/vendor/docs**.
- Read the surrounding code to answer: “Is this reachable in production?”
- Add 1–3 sentences to `triage_reason` describing the real-world risk *in this repo*.

Output requirement:

- Write the curated list to `out/findings.agent.json` as a JSON array using the same canonical schema fields.
- Each record should include `triage` in `{action_required, review, informational, suppressed}` and a short `triage_reason`.

### 4) Render a Unified Report (Mandatory)

Option A (local Python 3):

```bash
python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md
```

Option B (Dockerized Python):

PowerShell:

```powershell
docker run --rm -v "${repo}:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md
```

Bash:

```bash
docker run --rm -v "$PWD:/work" -w /work python:3.12-slim python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md
```

### 5) Run LAUNCH_SECURITY_CHECK (Mandatory)

Perform a targeted repository review for the 15 patterns above.

- Start with route and middleware discovery, then inspect auth, upload, logging, config, and secret-management paths.
- Use fast code search to find likely hot spots, but validate findings by reading the real control flow in handlers/services.
- Record credible findings in `out/manual-review.md` using the required fields: `severity`, `evidence`, `why this is dangerous`, `recommended fix`.
- Keep findings evidence-based and deployment-realistic.

### 6) Completion Checks

Confirm these files exist:

- `out/gitleaks.json`
- `out/semgrep.json`
- `out/osv.json`
- `out/trivy.json`
- `out/findings.agent.json`
- `out/report.md`
- `out/manual-review.md` (or an explicit note that no credible manual findings were identified)

If any raw scanner JSON is missing, treat the scan as **incomplete coverage** and rerun the missing scanner(s) (do not ship based on partial results).

### 7) Artifact Handling (Recommended)

Raw scanner outputs can contain sensitive information (especially `semgrep.json`, and sometimes `gitleaks.json` depending on tool behavior/version).

- Keep `out/` private.
- In CI, store artifacts only in secured storage with retention limits.
- After you’ve produced `out/report.md` (and optionally `out/report.json`), consider deleting the raw scanner outputs:

PowerShell:

```powershell
Remove-Item -Force out\gitleaks.json,out\semgrep.json,out\osv.json,out\trivy.json -ErrorAction SilentlyContinue
```

## How to Consume Results (For Inexperienced Engineers)

- Start with `out/report.md` → **Executive Summary** for a quick overview.
- Fix everything in **Action Required** first — these are high-confidence, high-severity issues in production code.
  - Secrets first: remove, rotate, and move to a secrets manager.
  - Then RCE/injection SAST issues.
  - Then high-severity dependency vulnerabilities.
- Review the **Worth Reviewing** section next — these need human judgment to determine if they're real issues.
- **Informational** findings are low-risk or in test/example code — address at your discretion.
- **Suppressed** findings are likely false positives — listed for auditability. Only revisit if your context differs from the suppression reason.

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

### Triage Tiers

| Tier | Meaning |
|------|---------|
| `action_required` | High-confidence, high-severity findings in production code. Fix these. |
| `review` | Medium severity or low confidence on high severity. Needs human judgment. |
| `informational` | Low risk, test code, vendored code, or below confidence threshold. |
| `suppressed` | Matched a known false-positive pattern. Listed for auditability. |

## CI Mode (Recommended)

### Gate on severity

Fail the job if any non-suppressed finding is at or above a severity threshold. Suppressed findings are excluded by default:

```bash
python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md --fail-on high
```

### Gate on triage tier

Fail the job if any finding is classified as action-required (requires `out/findings.agent.json` with `triage` fields):

```bash
python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md --fail-on-tier action_required
```

### Gate on secrets only

Fail if any secrets are found (regardless of severity):

```bash
python .github/skills/security-scan/scripts/render_report.py --input out/findings.agent.json --report-json out/report.json --report-md out/report.md --fail-on info --fail-on-category secrets
```

## Troubleshooting (Common)

- **Docker mount errors (Windows)**: ensure Docker Desktop is running and the drive is shared/allowed for file sharing.
- **Path with spaces**: keep the PowerShell commands exactly as written (quoted `-v "${repo}:/repo:ro"`).
- **Empty report**: confirm all four raw JSON files exist in `out/` before normalization.
- **Git Bash on Windows**: prefer PowerShell. If you must use Git Bash, you may need to disable path conversion for volume mounts (e.g., set `MSYS_NO_PATHCONV=1`).
