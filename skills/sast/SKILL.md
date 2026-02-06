---
name: "sast-scan"
description: "Static analysis for insecure code patterns using Semgrep (Docker-first). Trigger on: static analysis; insecure code; injection; is my code secure."
---

## Goal

Find insecure code patterns using Semgrep auto configuration and normalize results to the canonical schema.

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
  semgrep/semgrep:1.60.0 \
  semgrep --config auto --json --output /out/semgrep.json /repo
```

## Output normalization

- Read `/out/semgrep.json`.
- Map each finding to the canonical schema in `shared/CANONICAL_FINDING_SCHEMA.md`.
- Set:
  - `category = sast`
  - `tool = semgrep`
  - `title` from rule message
  - `file`, `start_line`, `end_line` from location
  - `severity` map: Semgrep `ERROR` -> `high`, `WARNING` -> `medium`, `INFO` -> `low`
  - `confidence` from rule metadata if provided, else `medium`
- `evidence` should be a short, non-sensitive snippet.
- Write normalized output to `/out/findings.sast.json`.

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
  semgrep/semgrep:1.60.0 \
  semgrep --config auto --json --output /out/semgrep.json /repo
```
