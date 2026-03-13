# code-security-skills

A reusable GitHub Copilot / VS Code **agent skill** for running a full security scan (secrets + SAST + SCA + IaC) and rendering a unified report.

## Available skill

- `security-scan` - Run Gitleaks, Semgrep, OSV-Scanner, and Trivy **sequentially**, normalize findings, and render a unified report.

## Install

### Option A: Per-repository (recommended)

Copy this folder into your repo:

- `.github/skills/security-scan/`

### Option B: Personal (across repos)

Copy `.github/skills/security-scan/` into one of the supported personal locations (varies by agent host), for example:

- `~/.copilot/skills/security-scan/`
- `~/.agents/skills/security-scan/`
- `~/.claude/skills/security-scan/`

## Invoke

In the agent chat, use any of these prompts:

- "Is my code secure?"
- "Run a full security scan."
- "Show me the scan results."

## Run Locally

From the repo root, run each scanner command sequentially (see `.github/skills/security-scan/SKILL.md`), then normalize and render the report:

```bash
python .github/skills/security-scan/scripts/normalize_findings.py --out-dir out
python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

## CI Usage (Optional)

- Fail the job if any finding is `high` or `critical`:

```bash
python .github/skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md --fail-on high
```

- Treat `out/` as sensitive (raw scanner outputs can contain secrets or code). Keep artifacts private with retention limits.

Tip: For reproducible CI, pin scanner Docker images to tags/digests (see `.github/skills/security-scan/SKILL.md`).

## Requirements

- Docker (for all scanners)
- Python 3 (for the reporting script)
