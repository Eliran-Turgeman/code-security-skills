---
name: secrets-scan
description: Detect leaked secrets using Gitleaks (Docker-first). Trigger on: detect secrets, leaked credentials, keys, tokens, is my code secure.
---

## Goal

Detect leaked credentials, keys, tokens, and other secrets in a repository using Gitleaks. Produce normalized findings in the canonical schema.

## Inputs

- Repo root mounted read-only at `/repo`
- Output directory mounted at `/out`
- Shared references:
  - `shared/DOCKER_IMAGES.md`
  - `shared/CANONICAL_FINDING_SCHEMA.md`
  - `shared/TRIAGE_RULES.md`

## Safety constraints

- Never print raw secrets. Always redact in `evidence`.
- Only read from `/repo:ro`.
- Write outputs only to `/out`.

## Tool invocation

Use the pinned image from `shared/DOCKER_IMAGES.md`.

Example command:

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:v8.18.2 \
  detect --source /repo --report-format json --report-path /out/gitleaks.json
```

## Output normalization

- Read `/out/gitleaks.json`.
- Map each finding to the canonical schema in `shared/CANONICAL_FINDING_SCHEMA.md`.
- Set:
  - `category = secrets`
  - `tool = gitleaks`
  - `title` from Gitleaks rule description
  - `file`, `start_line`, `end_line` from location
  - `severity` map: `critical` for high-confidence secrets, otherwise `high`
  - `confidence` from rule confidence if available; else `high`
- `evidence` must be redacted (e.g., `API_KEY=REDACTED`).
- Write normalized output to `/out/findings.secrets.json`.

## Prioritization

Apply `shared/TRIAGE_RULES.md` when sorting findings.

## User-facing report format

Provide a short summary and a table with:

- `severity`
- `title`
- `file:line`
- `remediation`

## How to rerun locally

```bash
mkdir -p out

docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:v8.18.2 \
  detect --source /repo --report-format json --report-path /out/gitleaks.json
```
