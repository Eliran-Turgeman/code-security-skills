# code-security-skills

A single, deterministic skill for running secrets, SAST, SCA, and IaC scans and rendering a unified report.

## Available skill

- `security-scan` - Run Gitleaks, Semgrep, OSV-Scanner, and Trivy and render a unified report.

## Install (Codex)

1. Copy `skills/security-scan` into your Codex skills directory:
   - Windows: `%USERPROFILE%\.codex\skills\security-scan`
   - macOS/Linux: `~/.codex/skills/security-scan`
2. Restart Codex so it reloads skills.

## Invoke (Codex)

In the agent chat, you can invoke the skill via `$security-scan` or prompts like these:

- "Is my code secure?"
- "Run a full security scan."
- "Show me the scan results."

## Requirements

- Docker (for all scanners)
- Python 3 (for the reporting script)
