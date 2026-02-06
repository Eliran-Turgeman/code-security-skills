# Report Format

The renderer produces two outputs:

## /out/report.json

- JSON array of canonical findings
- Sorted by triage rules
- De-duplicated by `id`

## /out/report.md

Sections (in order):

1. Summary
2. Top 10 Fixes
3. Findings by Category
4. Coverage Notes
5. Rerun Instructions

### Summary

Table with counts by category and severity.

### Top 10 Fixes

Top 10 findings after triage sorting.

### Findings by Category

Grouped lists with:

- severity
- title
- file:line
- remediation

### Coverage Notes

Notes about which inputs were included and any limitations.

### Rerun Instructions

Short guidance on re-running scanners and the report renderer.
