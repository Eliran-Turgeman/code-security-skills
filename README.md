# code-security-skills

A single, deterministic Codex skill for running secrets, SAST, SCA, and IaC scans in parallel and rendering a unified report.

## Available skill

- `security-scan` - Run Gitleaks, Semgrep, OSV-Scanner, and Trivy in parallel and render a unified report.

## Install (Codex)

1. Copy `skills/security-scan` into your Codex skills directory:
   - Windows: `%USERPROFILE%\.codex\skills\security-scan`
   - macOS/Linux: `~/.codex/skills/security-scan`
2. Restart Codex so it reloads skills.

## Invoke (Codex)

In the agent chat, use any of these prompts:

- "Is my code secure?"
- "Run a full security scan."
- "Show me the scan results."

## Run Locally

From the repo root, run each scanner command sequentially (see `skills/security-scan/SKILL.md`), then normalize and render the report:

```bash
python skills/security-scan/scripts/normalize_findings.py --out-dir out
python skills/security-scan/scripts/render_report.py --input-dir out --report-json out/report.json --report-md out/report.md
```

## Requirements

- Docker (for all scanners)
- Python 3 (for the reporting script)
