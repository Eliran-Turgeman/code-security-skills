# IaC Output Normalization

Normalize Trivy config results into the canonical schema.

## Mapping

- `id`: hash of `trivy` + `file` + `start_line` + `check_id`
- `category`: `iac`
- `severity`: from Trivy severity
- `confidence`: `medium`
- `tool`: `trivy`
- `title`: check title
- `file`: target file path
- `start_line`: start line if available; else `0`
- `end_line`: end line if available; else `0`
- `package`: null
- `version`: null
- `evidence`: short non-sensitive snippet
- `remediation`: use check description or recommended fix
