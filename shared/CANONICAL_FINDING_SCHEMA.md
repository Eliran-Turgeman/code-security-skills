# Canonical Finding Schema

All skills must normalize tool output to this schema. Output is an array of findings in JSON.

## Fields

- `id`: Stable hash derived from tool + file + location + rule id or fingerprint.
- `category`: `secrets` | `sast` | `sca` | `iac`
- `severity`: `critical` | `high` | `medium` | `low` | `info`
- `confidence`: `high` | `medium` | `low`
- `tool`: Scanner name (e.g., `gitleaks`, `semgrep`, `osv`, `trivy`)
- `title`: Short human-readable title
- `file`: Path relative to repo root
- `start_line`: 1-based line number
- `end_line`: 1-based line number
- `package`: Dependency name (SCA only; omit or null otherwise)
- `version`: Dependency version (SCA only; omit or null otherwise)
- `evidence`: Short snippet that avoids secrets; redact sensitive values
- `remediation`: Clear fix guidance

## JSON Example

```json
[
  {
    "id": "sha256:5a8f...",
    "category": "secrets",
    "severity": "critical",
    "confidence": "high",
    "tool": "gitleaks",
    "title": "AWS access key detected",
    "file": "src/config.js",
    "start_line": 12,
    "end_line": 12,
    "package": null,
    "version": null,
    "evidence": "AWS_ACCESS_KEY_ID=REDACTED",
    "remediation": "Remove the secret, rotate the key, and use environment variables or a secrets manager."
  }
]
```

## Normalization Rules

- Always include `id`, `category`, `severity`, `confidence`, `tool`, `title`, `file`.
- Use `null` for `package` and `version` when not applicable.
- Keep `evidence` to a short redacted snippet.
- Line numbers are required when the tool provides them; otherwise set to `0`.
