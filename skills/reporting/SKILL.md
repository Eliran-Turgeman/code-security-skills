---
name: report-findings
description: Render consistent scan results from normalized findings. Use after scans to summarize or show findings.
---

## Goal

Render deterministic, consistent scan reports from normalized findings without LLM-generated formatting.

## Inputs

- Normalized findings JSON files in `/out` (e.g., `findings.secrets.json`, `findings.sast.json`, `findings.sca.json`, `findings.iac.json`)
- Shared references:
  - `shared/CANONICAL_FINDING_SCHEMA.md`
  - `shared/TRIAGE_RULES.md`
  - `skills/reporting/references/REPORT_FORMAT.md`

## Safety constraints

- Do not emit raw secrets.
- Do not invent or drop fields. Use the script output as-is.

## Tool invocation

Use the bundled script to render the report:

```bash
python skills/reporting/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```

## Output

- `/out/report.json`: merged, triaged findings list
- `/out/report.md`: human-readable report in a consistent format

## How to rerun locally

```bash
python skills/reporting/scripts/render_report.py --input-dir /out --report-json /out/report.json --report-md /out/report.md
```