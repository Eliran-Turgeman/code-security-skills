#!/usr/bin/env python3
"""
Normalize scanner outputs into the canonical findings schema.

Inputs:
- gitleaks.json
- semgrep.json
- osv.json
- trivy.json

Outputs:
- findings.secrets.json
- findings.sast.json
- findings.sca.json
- findings.iac.json
"""

import argparse
import hashlib
import json
import os
from typing import Any, Dict, List


def sha_id(*parts: str) -> str:
    h = hashlib.sha256("|".join(parts).encode("utf-8"))
    return "sha256:" + h.hexdigest()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def norm_gitleaks(path: str) -> List[Dict[str, Any]]:
    data = load_json(path)
    if not isinstance(data, list):
        return []
    findings = []
    for item in data:
        rule_id = str(item.get("RuleID") or item.get("Rule") or "gitleaks")
        file_path = str(item.get("File") or "unknown")
        start_line = int(item.get("StartLine") or 0)
        end_line = int(item.get("EndLine") or start_line or 0)
        title = str(item.get("Description") or item.get("RuleDescription") or rule_id)
        confidence_raw = str(item.get("Confidence") or "high").lower()
        confidence = "high" if "high" in confidence_raw else "medium" if "medium" in confidence_raw else "low"
        severity = "critical" if confidence == "high" else "high"
        finding = {
            "id": sha_id("gitleaks", file_path, str(start_line), rule_id),
            "category": "secrets",
            "severity": severity,
            "confidence": confidence,
            "tool": "gitleaks",
            "title": title,
            "file": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "package": None,
            "version": None,
            "evidence": f"{rule_id} detected (redacted)",
            "remediation": "Remove the secret, rotate it, and store it in a secrets manager.",
        }
        findings.append(finding)
    return findings


def norm_semgrep(path: str) -> List[Dict[str, Any]]:
    data = load_json(path)
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []
    findings = []
    for item in results:
        rule_id = str(item.get("check_id") or item.get("rule_id") or "semgrep")
        path_val = item.get("path") or item.get("path") or "unknown"
        start = item.get("start", {}) or {}
        end = item.get("end", {}) or {}
        start_line = int(start.get("line") or 0)
        end_line = int(end.get("line") or start_line or 0)
        extra = item.get("extra", {}) or {}
        title = str(extra.get("message") or rule_id)
        sev_raw = str(extra.get("severity") or "info").upper()
        severity = "high" if sev_raw == "ERROR" else "medium" if sev_raw == "WARNING" else "low"
        conf_raw = str((extra.get("metadata", {}) or {}).get("confidence") or "medium").lower()
        confidence = "high" if "high" in conf_raw else "medium" if "medium" in conf_raw else "low"
        finding = {
            "id": sha_id("semgrep", str(path_val), str(start_line), rule_id),
            "category": "sast",
            "severity": severity,
            "confidence": confidence,
            "tool": "semgrep",
            "title": title,
            "file": str(path_val),
            "start_line": start_line,
            "end_line": end_line,
            "package": None,
            "version": None,
            "evidence": str(item.get("code") or ""),
            "remediation": str(extra.get("fix") or "Follow the Semgrep rule guidance."),
        }
        findings.append(finding)
    return findings


def _severity_from_osv(vuln: Dict[str, Any]) -> str:
    sev = vuln.get("severity")
    if isinstance(sev, list) and sev:
        # severity entries often contain {type, score}
        score = str(sev[0].get("score") or "").lower()
        if "critical" in score:
            return "critical"
        if "high" in score:
            return "high"
        if "medium" in score:
            return "medium"
        if "low" in score:
            return "low"
    return "medium"


def norm_osv(path: str) -> List[Dict[str, Any]]:
    data = load_json(path)
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []
    findings = []
    for res in results:
        packages = res.get("packages") or []
        vulns = res.get("vulnerabilities") or []
        for pkg in packages:
            pkg_name = str((pkg.get("package") or {}).get("name") or pkg.get("name") or "unknown")
            pkg_version = str(pkg.get("version") or "unknown")
            for vuln in vulns:
                vuln_id = str(vuln.get("id") or "OSV")
                title = str(vuln.get("summary") or vuln_id)
                severity = _severity_from_osv(vuln)
                finding = {
                    "id": sha_id("osv", pkg_name, pkg_version, vuln_id),
                    "category": "sca",
                    "severity": severity,
                    "confidence": "high",
                    "tool": "osv",
                    "title": title,
                    "file": str(res.get("source", {}).get("path") or "unknown"),
                    "start_line": 0,
                    "end_line": 0,
                    "package": pkg_name,
                    "version": pkg_version,
                    "evidence": f"{pkg_name}@{pkg_version} affected by {vuln_id}",
                    "remediation": "Upgrade to a fixed version if available.",
                }
                findings.append(finding)
    return findings


def norm_trivy(path: str) -> List[Dict[str, Any]]:
    data = load_json(path)
    results = data.get("Results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return []
    findings = []
    for res in results:
        misconfigs = res.get("Misconfigurations") or []
        for m in misconfigs:
            rule_id = str(m.get("ID") or "trivy")
            title = str(m.get("Title") or rule_id)
            severity = str(m.get("Severity") or "low").lower()
            cause = m.get("CauseMetadata") or {}
            start_line = int(cause.get("StartLine") or 0)
            end_line = int(cause.get("EndLine") or start_line or 0)
            finding = {
                "id": sha_id("trivy", str(res.get("Target") or "unknown"), str(start_line), rule_id),
                "category": "iac",
                "severity": severity,
                "confidence": "medium",
                "tool": "trivy",
                "title": title,
                "file": str(res.get("Target") or "unknown"),
                "start_line": start_line,
                "end_line": end_line,
                "package": None,
                "version": None,
                "evidence": str(m.get("Message") or ""),
                "remediation": str(m.get("Resolution") or "Apply the recommended fix."),
            }
            findings.append(finding)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize scanner outputs to canonical findings.")
    parser.add_argument("--out-dir", default="out", help="Output directory containing scanner JSON files")
    args = parser.parse_args()

    out_dir = args.out_dir
    gitleaks_path = os.path.join(out_dir, "gitleaks.json")
    semgrep_path = os.path.join(out_dir, "semgrep.json")
    osv_path = os.path.join(out_dir, "osv.json")
    trivy_path = os.path.join(out_dir, "trivy.json")

    if os.path.exists(gitleaks_path):
        write_json(os.path.join(out_dir, "findings.secrets.json"), norm_gitleaks(gitleaks_path))
    if os.path.exists(semgrep_path):
        write_json(os.path.join(out_dir, "findings.sast.json"), norm_semgrep(semgrep_path))
    if os.path.exists(osv_path):
        write_json(os.path.join(out_dir, "findings.sca.json"), norm_osv(osv_path))
    if os.path.exists(trivy_path):
        write_json(os.path.join(out_dir, "findings.iac.json"), norm_trivy(trivy_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
