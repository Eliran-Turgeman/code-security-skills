---
name: iac-scan
description: IaC and configuration scanning using Trivy config (Docker-first). Trigger on: IaC, terraform, k8s, dockerfile, github actions, configuration security, is my code secure.
---

## Goal

Detect insecure infrastructure and configuration issues across IaC and config files using Trivy config.

## Inputs

- Repo root mounted read-only at `/repo`
- Output directory mounted at `/out`
- Shared references:
  - `shared/DOCKER_IMAGES.md`
  - `shared/CANONICAL_FINDING_SCHEMA.md`
  - `shared/TRIAGE_RULES.md`

## Safety constraints

- Only read from `/repo:ro`.
- Write outputs only to `/out`.

## Tool invocation

Use the pinned image from `shared/DOCKER_IMAGES.md`.

Example command:

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  aquasec/trivy:0.50.1 \
  config --format json -o /out/trivy.json /repo
```

## Output normalization

- Read `/out/trivy.json`.
- Map each finding to the canonical schema in `shared/CANONICAL_FINDING_SCHEMA.md`.
- Set:
  - `category = iac`
  - `tool = trivy`
  - `title` from check title
  - `file`, `start_line`, `end_line` from location if available
  - `severity` from Trivy severity
  - `confidence = medium`
- `package` and `version` should be null.
- Write normalized output to `/out/findings.iac.json`.

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
  aquasec/trivy:0.50.1 \
  config --format json -o /out/trivy.json /repo
```
