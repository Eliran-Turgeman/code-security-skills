# Triage Rules

These rules define prioritization across categories. All skills and the full scan must apply them when sorting findings.

## Priority Order (Highest to Lowest)

1. Secrets (any severity)
2. RCE and injection issues (SAST)
3. SSRF and auth bypass (SAST)
4. Runtime dependency vulnerabilities (SCA)
5. Public IaC exposure or overly permissive access (IaC)
6. All other findings by severity

## Severity Sort

Within each priority group, sort by severity:

`critical` > `high` > `medium` > `low` > `info`

## Confidence Sort

Within same severity, sort by confidence:

`high` > `medium` > `low`

## De-duplication

- Findings with the same `id` are considered duplicates.
- Prefer the finding with the higher severity or confidence.
