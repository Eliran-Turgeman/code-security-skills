# SAST Output Normalization

Normalize Semgrep findings into the canonical schema.

## Mapping

- `id`: hash of `semgrep` + `file` + `start_line` + `rule_id`
- `category`: `sast`
- `severity`: map Semgrep level
  - `ERROR` -> `high`
  - `WARNING` -> `medium`
  - `INFO` -> `low`
- `confidence`: use rule metadata confidence if present; else `medium`
- `tool`: `semgrep`
- `title`: rule message
- `file`: `path`
- `start_line`: `start.line`
- `end_line`: `end.line`
- `package`: null
- `version`: null
- `evidence`: short snippet, avoid secrets
- `remediation`: use rule message or fix guidance if available
