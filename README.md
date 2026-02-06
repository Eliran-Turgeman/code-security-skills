# code-security-skills

A repository of deterministic, Docker-first security scanning skills that standardize how agents run common scanners and normalize findings into a shared schema.

## How agents use this repo

Agents load skills from `skills/` and choose the appropriate skill based on user intent. The single skill runs all scanners in parallel, normalizes output to a canonical finding schema, and produces a structured report.

## Available skills

- `security-scan` - Run secrets, SAST, SCA, and IaC scans in parallel and render a unified report.

## Example user flows

User: "Is my code secure?"
Agent: invokes `skills/security-scan/SKILL.md`

User: "Run a full security scan"
Agent: invokes `skills/security-scan/SKILL.md`

User: "Show me the scan results"
Agent: invokes `skills/security-scan/SKILL.md`

## Philosophy

This repo does not replace scanners. It standardizes how agents run them.

Focus areas:

- Determinism
- Explainability
- Prioritization
- Developer UX

## Repository structure

```
code-security-skills/
  README.md

  skills/
    security-scan/
      SKILL.md
      agents/
        openai.yaml
      scripts/
        render_report.py
      references/
        REPORT_FORMAT.md
```
