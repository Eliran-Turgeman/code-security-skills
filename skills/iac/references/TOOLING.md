# Trivy Config Tooling

## Purpose

Scan IaC and configuration files for insecure settings (Terraform, Kubernetes, Dockerfile, GitHub Actions, etc.).

## Docker Invocation

```bash
docker run --rm \
  -v "$PWD:/repo:ro" \
  -v "$PWD/out:/out" \
  aquasec/trivy:0.50.1 \
  config --format json -o /out/trivy.json /repo
```

## Output

- JSON report written to `/out/trivy.json`
- Normalize to canonical findings in `/out/findings.iac.json`
