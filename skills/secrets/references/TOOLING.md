# Gitleaks Tooling

## Purpose

Scan the repository for leaked secrets, keys, and tokens.

## Docker Invocation

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  zricethezav/gitleaks:v8.18.2 \
  detect --source /repo --report-format json --report-path /out/gitleaks.json
```

## Output

- JSON report written to `/out/gitleaks.json`
- Normalize to canonical findings in `/out/findings.secrets.json`
