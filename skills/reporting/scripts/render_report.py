#!/usr/bin/env python3
"""
Deterministic report renderer for canonical security findings.

- Merges findings from one or more inputs
- De-duplicates by id
- Applies triage sorting rules
- Emits /out/report.json and /out/report.md
"""

import argparse
import json
import os
import sys
from collections import defaultdict

SEVERITY_ORDER = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
CONFIDENCE_ORDER = {"high": 3, "medium": 2, "low": 1}

CATEGORY_PRIORITY = {
    "secrets": 1,
    "sast_rce_injection": 2,
    "sast_ssrf_auth_bypass": 3,
    "sca_runtime": 4,
    "iac_public_exposure": 5,
    "other": 6,
}

RCE_INJECTION_KEYWORDS = [
    "rce",
    "remote code execution",
    "command injection",
    "sql injection",
    "os command injection",
    "code injection",
    "deserialization",
    "xxe",
    "ssti",
    "template injection",
]

SSRF_AUTH_BYPASS_KEYWORDS = [
    "ssrf",
    "server-side request forgery",
    "auth bypass",
    "authentication bypass",
    "authorization bypass",
    "privilege escalation",
]

IAC_PUBLIC_EXPOSURE_KEYWORDS = [
    "public",
    "0.0.0.0/0",
    "world-writable",
    "open to the internet",
    "publicly accessible",
    "public access",
]


def load_findings(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def normalize_line(value):
    try:
        return int(value)
    except Exception:
        return 0


def classify_priority(finding):
    category = (finding.get("category") or "").lower()
    title = (finding.get("title") or "").lower()

    if category == "secrets":
        return "secrets"

    if category == "sast":
        if any(k in title for k in RCE_INJECTION_KEYWORDS):
            return "sast_rce_injection"
        if any(k in title for k in SSRF_AUTH_BYPASS_KEYWORDS):
            return "sast_ssrf_auth_bypass"

    if category == "sca":
        return "sca_runtime"

    if category == "iac":
        if any(k in title for k in IAC_PUBLIC_EXPOSURE_KEYWORDS):
            return "iac_public_exposure"

    return "other"


def triage_sort_key(finding):
    priority_bucket = classify_priority(finding)
    severity = (finding.get("severity") or "info").lower()
    confidence = (finding.get("confidence") or "low").lower()
    title = (finding.get("title") or "").lower()
    return (
        CATEGORY_PRIORITY.get(priority_bucket, CATEGORY_PRIORITY["other"]),
        -SEVERITY_ORDER.get(severity, 0),
        -CONFIDENCE_ORDER.get(confidence, 0),
        title,
    )


def dedupe_findings(findings):
    by_id = {}
    for f in findings:
        fid = f.get("id") or ""
        if not fid:
            continue
        existing = by_id.get(fid)
        if existing is None:
            by_id[fid] = f
            continue
        # Keep higher severity/confidence
        def score(x):
            sev = (x.get("severity") or "info").lower()
            conf = (x.get("confidence") or "low").lower()
            return (SEVERITY_ORDER.get(sev, 0), CONFIDENCE_ORDER.get(conf, 0))

        if score(f) > score(existing):
            by_id[fid] = f
    return list(by_id.values())


def summarize(findings):
    counts = defaultdict(lambda: defaultdict(int))
    for f in findings:
        category = (f.get("category") or "unknown").lower()
        severity = (f.get("severity") or "info").lower()
        counts[category][severity] += 1
    return counts


def format_summary_table(counts):
    severities = ["critical", "high", "medium", "low", "info"]
    categories = sorted(counts.keys())
    lines = []
    header = "| Category | " + " | ".join(s.title() for s in severities) + " | Total |"
    sep = "|---" * (len(severities) + 2) + "|"
    lines.append(header)
    lines.append(sep)
    for cat in categories:
        total = sum(counts[cat].values())
        row = [cat] + [str(counts[cat].get(s, 0)) for s in severities] + [str(total)]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def format_finding_row(f):
    file_path = f.get("file") or "unknown"
    start_line = normalize_line(f.get("start_line"))
    loc = f"{file_path}:{start_line}" if start_line else file_path
    remediation = f.get("remediation") or "See tool guidance"
    return f"- **{f.get('severity', 'info').lower()}** {f.get('title', 'Untitled')} ({loc})\n  Remediation: {remediation}"


def write_report_md(path, findings, coverage_notes, rerun_notes):
    counts = summarize(findings)
    summary_table = format_summary_table(counts) if counts else "No findings."

    top_10 = findings[:10]
    top_10_lines = "\n".join(format_finding_row(f) for f in top_10) if top_10 else "No findings."

    by_category = defaultdict(list)
    for f in findings:
        by_category[(f.get("category") or "unknown").lower()].append(f)

    sections = []
    sections.append("# Security Scan Report")
    sections.append("")
    sections.append("## Summary")
    sections.append("")
    sections.append(summary_table)
    sections.append("")
    sections.append("## Top 10 Fixes")
    sections.append("")
    sections.append(top_10_lines)
    sections.append("")
    sections.append("## Findings by Category")
    sections.append("")

    for cat in sorted(by_category.keys()):
        sections.append(f"### {cat}")
        sections.append("")
        sections.append("\n".join(format_finding_row(f) for f in by_category[cat]))
        sections.append("")

    sections.append("## Coverage Notes")
    sections.append("")
    sections.append("\n".join(f"- {note}" for note in coverage_notes))
    sections.append("")
    sections.append("## Rerun Instructions")
    sections.append("")
    sections.append("\n".join(f"- {note}" for note in rerun_notes))
    sections.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(sections))


def main():
    parser = argparse.ArgumentParser(description="Render a consistent security scan report.")
    parser.add_argument(
        "--input",
        action="append",
        dest="inputs",
        help="Path to normalized findings JSON. Can be repeated.",
    )
    parser.add_argument(
        "--input-dir",
        default="/out",
        help="Directory containing findings.*.json files (default: /out).",
    )
    parser.add_argument(
        "--report-json",
        default="/out/report.json",
        help="Output path for merged JSON report (default: /out/report.json).",
    )
    parser.add_argument(
        "--report-md",
        default="/out/report.md",
        help="Output path for markdown report (default: /out/report.md).",
    )
    args = parser.parse_args()

    inputs = list(args.inputs or [])
    if not inputs:
        if os.path.isdir(args.input_dir):
            for name in os.listdir(args.input_dir):
                if name.startswith("findings.") and name.endswith(".json"):
                    inputs.append(os.path.join(args.input_dir, name))

    if not inputs:
        print("No input files found.", file=sys.stderr)
        return 2

    findings = []
    for path in sorted(inputs):
        findings.extend(load_findings(path))

    findings = dedupe_findings(findings)
    findings.sort(key=triage_sort_key)

    os.makedirs(os.path.dirname(args.report_json), exist_ok=True)
    with open(args.report_json, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    coverage_notes = [
        f"Inputs: {', '.join(os.path.basename(p) for p in inputs)}",
        "Findings are normalized to the canonical schema.",
        "No raw secrets are included in evidence.",
    ]

    rerun_notes = [
        "Run the scanner-specific Docker commands from the corresponding skills.",
        "Ensure /out contains findings.*.json before rendering the report.",
    ]

    write_report_md(args.report_md, findings, coverage_notes, rerun_notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
