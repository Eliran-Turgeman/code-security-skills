# SCA Output Normalization

Normalize OSV-Scanner results into the canonical schema.

## Mapping

- `id`: hash of `osv` + `package` + `version` + `vuln_id`
- `category`: `sca`
- `severity`: from OSV severity if available, else `medium`
- `confidence`: `high`
- `tool`: `osv`
- `title`: vulnerability summary or ID
- `file`: manifest or lockfile path if present; else `unknown`
- `start_line`: `0`
- `end_line`: `0`
- `package`: package name
- `version`: affected version
- `evidence`: short note such as "Package X@Y affected by OSV-XXXX"
- `remediation`: upgrade to a fixed version if available
