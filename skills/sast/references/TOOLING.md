# Semgrep Tooling

## Purpose

Static analysis for insecure code patterns across languages using Semgrep auto configuration.

## Docker Invocation

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  semgrep/semgrep:1.60.0 \
  semgrep --config auto --json --output /out/semgrep.json /repo
```

## Output

- JSON report written to `/out/semgrep.json`
- Normalize to canonical findings in `/out/findings.sast.json`
