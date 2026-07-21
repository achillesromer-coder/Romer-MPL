#!/usr/bin/env python3
"""Static release-gate audit for the single-file Römer MPL application.

The audit is intentionally non-destructive. It inventories source lineage,
regulatory-language conflicts, trust-boundary risks, deterministic logic bugs,
and evidence/provenance gaps in index.html. It does not certify regulatory
compliance or validate physical/flight-safety models.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class Finding:
    finding_id: str
    severity: str
    state: str
    title: str
    evidence: str
    release_effect: str
    next_action: str


class _IdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key == "id" and value:
                self.ids.append(value)


def _count(source: str, pattern: str, *, flags: int = 0) -> int:
    return len(re.findall(pattern, source, flags))


def _present(source: str, pattern: str, *, flags: int = 0) -> bool:
    return re.search(pattern, source, flags) is not None


def duplicate_html_ids(source: str) -> list[str]:
    parser = _IdParser()
    parser.feed(source)
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in parser.ids:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def audit_source(source: str) -> list[Finding]:
    findings: list[Finding] = []

    if not _present(source, r'<meta\s+name=["\']robots["\']\s+content=["\']noindex["\']', flags=re.I):
        findings.append(Finding(
            "MPL-PUB-001", "HIGH", "FAIL",
            "No noindex release control",
            "The source does not contain a robots noindex directive.",
            "Public indexing could occur before the release gate is approved.",
            "Keep the route noindex until soft-launch approval."
        ))

    year_2019 = _present(source, r"ASA(?:\s+MPL|\s+METHODOLOGY)?[^\n]{0,40}2019", flags=re.I)
    year_2024 = _present(source, r"ASA(?:\s+MPL|\s+CONSTANTS)?[^\n]{0,40}2024", flags=re.I)
    if year_2019 and year_2024:
        findings.append(Finding(
            "MPL-REG-001", "CRITICAL", "FAIL",
            "Conflicting ASA methodology years",
            "The same build identifies the MPL basis as both 2019 and 2024.",
            "Regulatory-compliance wording is not releaseable until provenance is singular and cited.",
            "Set one methodology identifier and attach source/version receipts for every constant."
        ))

    if _present(source, r"ASA-compliant|ASA MPL\s+[—-]\s+\$\{?r\.compliance", flags=re.I):
        findings.append(Finding(
            "MPL-CLAIM-001", "CRITICAL", "REVIEW_REQUIRED",
            "Unqualified regulatory-compliance language",
            "The UI or metadata describes the application/output as ASA-compliant.",
            "A model result may be mistaken for regulator acceptance or an application-ready determination.",
            "Use controlled wording such as MODEL CHECK only until independent regulatory review passes."
        ))

    if _present(source, r"iip-prob[^\n]*textContent\s*=\s*['\"]<\s*1×10⁻⁷", flags=re.I):
        findings.append(Finding(
            "MPL-CLAIM-002", "CRITICAL", "FAIL",
            "Hard-coded probability display",
            "The IIP probability badge is set to < 1×10⁻⁷ without a calculation result.",
            "The interface can display a safety threshold as if demonstrated.",
            "Bind the display to a verified probability calculation or show NOT CALCULATED."
        ))

    if _present(source, r"const\s+dist\s*=\s*simData\.alt\s*\*\s*2\.8"):
        findings.append(Finding(
            "MPL-MODEL-001", "HIGH", "REVIEW_REQUIRED",
            "Simplified IIP propagation presented beside regulatory outputs",
            "Downrange distance is estimated as altitude multiplied by 2.8 before great-circle projection.",
            "A screening visualization may be mistaken for a flight-safety trajectory product.",
            "Label the IIP path SCREENING/ILLUSTRATIVE and validate against an approved trajectory source."
        ))

    risk_shape = _present(source, r"riskHeatPoints\.push\(\{[^}]*risk\s*:")
    risk_read = _present(source, r"latest\.zone\s*===")
    if risk_shape and risk_read:
        findings.append(Finding(
            "MPL-BUG-001", "HIGH", "FAIL",
            "Risk-heat color reads a missing property",
            "Risk points store a risk object, but color selection reads latest.zone.",
            "Risk heat may fall through to the wrong color/category.",
            "Store zone explicitly or read the stored risk/zone field consistently; add regression tests."
        ))

    if _present(source, r"timeToFail\s*>\s*30\s*\?\s*['\"]NOMINAL['\"]\s*:\s*timeToFail\s*>\s*5\s*\?\s*['\"]CAUTION['\"]\s*:\s*['\"]NOMINAL['\"]"):
        findings.append(Finding(
            "MPL-BUG-002", "HIGH", "FAIL",
            "FSS countdown returns to NOMINAL immediately before failure",
            "For five seconds or less to failure, the status expression emits NOMINAL.",
            "The operator display can understate an imminent failure condition.",
            "Return WARNING/FAILURE-IMMINENT and test all boundary values."
        ))

    no_cors = _present(source, r"mode\s*:\s*['\"]no-cors['\"]")
    webhook_success = _present(source, r"Webhook dispatched")
    if no_cors and webhook_success:
        findings.append(Finding(
            "MPL-SEC-001", "HIGH", "FAIL",
            "Opaque webhook request is reported as verified success",
            "Webhook dispatch uses no-cors and then displays a success toast.",
            "The response cannot be inspected, so delivery is not proven.",
            "Report ATTEMPTED unless a verifiable acknowledgement/receipt is returned."
        ))

    if _present(source, r"webhookUrl\s*\|\|\s*['\"]['\"]") and _present(source, r"startsWith\(['\"]http['\"]\)"):
        findings.append(Finding(
            "MPL-SEC-002", "HIGH", "REVIEW_REQUIRED",
            "Arbitrary imported webhook destination",
            "The trust check accepts any imported URL beginning with http.",
            "Mission/operator/risk data can be sent to an unintended external endpoint.",
            "Require HTTPS, explicit operator confirmation, allowlisting or per-destination approval, and audit receipts."
        ))

    if _present(source, r"\.innerHTML\s*=\s*`") or _present(source, r"\.innerHTML\s*\+="):
        findings.append(Finding(
            "MPL-SEC-003", "HIGH", "REVIEW_REQUIRED",
            "Dynamic HTML interpolation requires escaping review",
            "The application builds multiple UI/report surfaces with innerHTML/template interpolation.",
            "Imported, sheet-derived or custom text may cross an HTML injection boundary.",
            "Centralize escaping/safe DOM construction and add hostile-input regression tests."
        ))

    if _present(source, r"RESTRICTED\s+[—-]\s+REGULATORY USE ONLY", flags=re.I):
        findings.append(Finding(
            "MPL-CLAIM-003", "HIGH", "REVIEW_REQUIRED",
            "Report classification implies regulatory readiness",
            "Generated reports are marked RESTRICTED — REGULATORY USE ONLY.",
            "Users may infer application suitability despite unverified/synthetic fallback data.",
            "Replace with CONTROLLED MODEL OUTPUT — NOT FOR APPLICATION until the evidence gate passes."
        ))

    if _present(source, r"const\s+ASA\s*=\s*\{"):
        findings.append(Finding(
            "MPL-PROV-001", "HIGH", "OPEN",
            "Embedded constants lack machine-readable source receipts",
            "Regulatory/economic constants are embedded in index.html comments.",
            "A run cannot prove which source revision, authority or uncertainty supported each value.",
            "Add a versioned constant registry with source URL, publication date, section, units and review status."
        ))

    if not _present(source, r"sourceHash|source_hash|modelHash|model_hash|commitSha|commit_sha"):
        findings.append(Finding(
            "MPL-PROV-002", "MEDIUM", "OPEN",
            "Run/report lacks immutable model-source identifier",
            "No source/model hash field was detected in run or report data.",
            "A result cannot be reproduced against the exact code/data revision.",
            "Add Git commit/blob hash, data snapshot IDs, method version and timestamp to every run receipt."
        ))

    for pattern, expected_id, label in (
        (r"const\s+MPL_SHEET_ID\s*=\s*['\"][^'\"]+['\"]", "MPL-SRC-001", "MPL Sheet ID"),
        (r"const\s+DRIVE_FOLDER\s*=\s*['\"][^'\"]+['\"]", "MPL-SRC-002", "Drive folder ID"),
        (r"const\s+APPS_SCRIPT\s*=\s*['\"]https://script\.google\.com/", "MPL-SRC-003", "Apps Script endpoint"),
    ):
        if not _present(source, pattern):
            findings.append(Finding(
                expected_id, "CRITICAL", "FAIL",
                "Locked integration declaration missing",
                f"Expected non-empty declaration for {label} was not found.",
                "The route may point at the wrong data/authority surface.",
                "Restore only after owner/source verification."
            ))

    duplicates = duplicate_html_ids(source)
    if duplicates:
        findings.append(Finding(
            "MPL-DOM-001", "MEDIUM", "FAIL",
            "Duplicate HTML element IDs",
            ", ".join(duplicates[:20]),
            "DOM lookups and event bindings can target the wrong element.",
            "Make IDs unique and add a static DOM-ID test."
        ))

    calc_count = _count(source, r"function\s+calculateMPL\s*\(")
    if calc_count != 1:
        findings.append(Finding(
            "MPL-CODE-001", "CRITICAL", "FAIL",
            "Unexpected calculateMPL definition count",
            f"Detected {calc_count} definitions.",
            "Duplicate/redefined engines can make runtime behavior depend on declaration order.",
            "Retain exactly one canonical calculation entry point."
        ))

    return findings


def summary(findings: Sequence[Finding]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    release_blocked = any(
        finding.severity in {"CRITICAL", "HIGH"}
        and finding.state in {"FAIL", "REVIEW_REQUIRED"}
        for finding in findings
    )
    return {
        "release_gate": "BLOCKED" if release_blocked else "REVIEW",
        "finding_count": len(findings),
        "severity_counts": counts,
    }


def audit_file(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    findings = audit_source(source)
    return {
        "schema_version": "1.0",
        "target": str(path),
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "line_count": source.count("\n") + 1,
        **summary(findings),
        "findings": [asdict(finding) for finding in findings],
        "limitations": [
            "Static source audit only.",
            "Does not prove live deployment identity, network integrations, browser rendering, regulatory compliance, or model validity.",
        ],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="index.html")
    parser.add_argument("--output", "-o")
    parser.add_argument("--strict", action="store_true", help="exit 1 when the release gate is blocked")
    args = parser.parse_args(argv)

    result = audit_file(Path(args.path))
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 1 if args.strict and result["release_gate"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
