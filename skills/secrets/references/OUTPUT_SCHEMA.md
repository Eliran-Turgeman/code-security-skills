# Secrets Output Normalization

Normalize Gitleaks findings into the canonical schema.

## Mapping

- `id`: hash of `gitleaks` + `file` + `start_line` + `rule_id`
- `category`: `secrets`
- `severity`: `critical` if rule is high-confidence secret; otherwise `high`
- `confidence`: from Gitleaks `Confidence` if present; else `high`
- `tool`: `gitleaks`
- `title`: rule description
- `file`: `File`
- `start_line`: `StartLine`
- `end_line`: `EndLine`
- `package`: null
- `version`: null
- `evidence`: redacted snippet
- `remediation`: remove secret, rotate, use secrets manager

## Redaction

Always redact secret values in `evidence`.
