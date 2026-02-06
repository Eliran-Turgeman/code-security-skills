# code-security-skills

A repository of deterministic, Docker-first security scanning skills that standardize how agents run common scanners and normalize findings into a shared schema.

## Available skills

- `secrets` - Detect leaked credentials, keys, and tokens using Gitleaks.
- `sast` - Static analysis for insecure code patterns using Semgrep (auto config).
- `sca` - Dependency vulnerability scanning using OSV-Scanner.
- `iac` - Infrastructure and configuration scanning using Trivy config.
- `full-scan` - Orchestrates all scans sequentially and produces a unified report.

