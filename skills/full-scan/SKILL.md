---
name: full-security-scan
description: Run secrets, SAST, SCA, and IaC scans then produce a unified report. Use for full or comprehensive security scans.
---

## Goal

Run secrets, SAST, SCA, and IaC scans sequentially and produce a unified report with triaged findings.

## Inputs

- Repo root mounted read-only at `/repo`
- Output directory mounted at `/out`
- Shared references:
  - `shared/DOCKER_IMAGES.md`
  - `shared/CANONICAL_FINDING_SCHEMA.md`
  - `shared/TRIAGE_RULES.md`
  - `skills/reporting/SKILL.md`

## Safety constraints

- Only read from `/repo:ro`.
- Write outputs only to `/out`.
- Never print raw secrets.

## Tool invocation

Run the following skills in order:

1. `skills/secrets/SKILL.md`
2. `skills/sast/SKILL.md`
3. `skills/sca/SKILL.md`
4. `skills/iac/SKILL.md`
5. `skills/reporting/SKILL.md`

Each scan skill writes normalized output to:

- `/out/findings.secrets.json`
- `/out/findings.sast.json`
- `/out/findings.sca.json`
- `/out/findings.iac.json`

Then run the reporting script for deterministic output:

```bash
python skills/reporting/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```

## Output normalization

- Merge all normalized findings into a single array.
- De-duplicate by `id`.
- Apply `shared/TRIAGE_RULES.md` sorting.
- Write unified output to `/out/report.json`.
- Write a consistent markdown report to `/out/report.md`.

## User-facing report format

The report format is defined in `skills/reporting/references/REPORT_FORMAT.md`.

## Prioritization

Apply `shared/TRIAGE_RULES.md` globally across all categories.

## How to rerun locally

```bash
mkdir -p out

# Secrets
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:v8.18.2 \
  detect --source /repo --report-format json --report-path /out/gitleaks.json

# SAST
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  semgrep/semgrep:1.60.0 \
  semgrep --config auto --json --output /out/semgrep.json /repo

# SCA
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  ghcr.io/google/osv-scanner:v1.7.1 \
  --format json -o /out/osv.json --recursive /repo

# IaC
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  aquasec/trivy:0.50.1 \
  config --format json -o /out/trivy.json /repo

# Report
python skills/reporting/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```