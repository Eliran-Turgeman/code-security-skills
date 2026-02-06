# Docker Images (Pinned)

All scanners must run via Docker, with pinned versions. Skills reference these image tags.

- gitleaks: zricethezav/gitleaks:v8.18.2
- semgrep: semgrep/semgrep:1.60.0
- osv: ghcr.io/google/osv-scanner:v1.7.1
- trivy: aquasec/trivy:0.50.1

Required runtime conventions:

- Mount repo read-only at `/repo:ro`
- Write outputs to `/out`
- No native installs
