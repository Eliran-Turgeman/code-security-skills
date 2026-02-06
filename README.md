# code-security-skills

A repository of deterministic, Docker-first security scanning skills that standardize how agents run common scanners and normalize findings into a shared schema.

## How agents use this repo

Agents load skills from `skills/` and choose the appropriate skill based on user intent. Each skill runs a specific scanner, normalizes output to a canonical finding schema, and produces structured, reproducible results.

## Available skills

- `secrets` - Detect leaked credentials, keys, and tokens using Gitleaks.
- `sast` - Static analysis for insecure code patterns using Semgrep (auto config).
- `sca` - Dependency vulnerability scanning using OSV-Scanner.
- `iac` - Infrastructure and configuration scanning using Trivy config.
- `reporting` - Deterministic reporting from normalized findings.
- `full-scan` - Orchestrates all scans sequentially and produces a unified report.

## Example user flows

User: "Is my code secure?"
Agent: invokes `skills/full-scan/SKILL.md`

User: "Do I have secrets?"
Agent: invokes `skills/secrets/SKILL.md`

User: "Show me the scan results"
Agent: invokes `skills/reporting/SKILL.md`

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
    secrets/
      SKILL.md
      references/
        TOOLING.md
        OUTPUT_SCHEMA.md

    sast/
      SKILL.md
      references/
        TOOLING.md
        OUTPUT_SCHEMA.md

    sca/
      SKILL.md
      references/
        TOOLING.md
        OUTPUT_SCHEMA.md

    iac/
      SKILL.md
      references/
        TOOLING.md
        OUTPUT_SCHEMA.md

    reporting/
      SKILL.md
      scripts/
        render_report.py
      references/
        REPORT_FORMAT.md

    full-scan/
      SKILL.md

  shared/
    CANONICAL_FINDING_SCHEMA.md
    TRIAGE_RULES.md
    DOCKER_IMAGES.md
```
