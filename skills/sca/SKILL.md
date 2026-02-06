---
name: sca-scan
description: Dependency vulnerability scanning using OSV-Scanner (Docker-first). Trigger on: dependency vulnerabilities, SCA, vulnerable packages, is my code secure.
---

## Goal

Identify vulnerable dependencies across ecosystems and normalize results to the canonical schema.

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
  ghcr.io/google/osv-scanner:v1.7.1 \
  --format json -o /out/osv.json --recursive /repo
```

## Output normalization

- Read `/out/osv.json`.
- Map each finding to the canonical schema in `shared/CANONICAL_FINDING_SCHEMA.md`.
- Set:
  - `category = sca`
  - `tool = osv`
  - `title` from vulnerability summary or ID
  - `package` and `version` from affected dependency
  - `severity` from OSV severity if present; else `medium`
  - `confidence = high`
- `file` should point to the manifest or lockfile if available; else `unknown`.
- `start_line` and `end_line` set to `0` if not provided.
- Write normalized output to `/out/findings.sca.json`.

## Prioritization

Apply `shared/TRIAGE_RULES.md` when sorting findings.

## User-facing report format

Provide a short summary and a table with:

- `severity`
- `package@version`
- `title`
- `remediation`

## How to rerun locally

```bash
mkdir -p out

docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  ghcr.io/google/osv-scanner:v1.7.1 \
  --format json -o /out/osv.json --recursive /repo
```
