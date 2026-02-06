# OSV-Scanner Tooling

## Purpose

Dependency vulnerability scanning across ecosystems and lockfiles.

## Docker Invocation

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  ghcr.io/google/osv-scanner:v1.7.1 \
  --format json -o /out/osv.json --recursive /repo
```

## Output

- JSON report written to `/out/osv.json`
- Normalize to canonical findings in `/out/findings.sca.json`
