# code-security-skills

This repository contains **agent skills only**.

## Available Skills

- `security-scan`
  - Run Gitleaks, Semgrep, OSV-Scanner, and Trivy sequentially.
  - Normalize findings and render unified reports.
  - Run `LAUNCH_SECURITY_CHECK` to review behavioral and architectural risks that static tools often miss.

## Install

### Per-repository (recommended)

Copy this folder into your repo:

- `.github/skills/security-scan/`

### Personal (across repos)

Copy `.github/skills/security-scan/` into one of the supported personal locations (varies by agent host), for example:

- `~/.copilot/skills/security-scan/`
- `~/.agents/skills/security-scan/`
- `~/.claude/skills/security-scan/`

## Invoke

In the agent chat, you can invoke the skill via `$security-scan` or prompts like these:

- "Is my code secure?"
- "Run a full security scan."
- "Run LAUNCH_SECURITY_CHECK and summarize critical risks."

## Skill Reference

For full behavior, required outputs, and operating procedure, see:

- `.github/skills/security-scan/SKILL.md`
