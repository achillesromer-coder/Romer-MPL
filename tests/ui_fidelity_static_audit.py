#!/usr/bin/env python3
"""Static UI/fidelity contract for the Römer MPL pre-release surface.

This audit intentionally separates hard, already-established interface invariants from
advisory refinement opportunities. A PASS here is a source/UI contract receipt only;
it is not empirical, regulatory, specialist, browser-provider or public-release proof.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


def contains(pattern: str, source: str, flags: int = 0) -> bool:
    return re.search(pattern, source, flags) is not None


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
    source = path.read_text(encoding="utf-8")
    sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    hard_contracts = {
        "pre_release_title": "<title>Römer MPL Platform — Pre-release</title>" in source,
        "viewport_present": contains(r'<meta\s+name=["\']viewport["\']', source, re.I),
        "viewport_does_not_disable_zoom": not contains(r'user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:[.0]*)?(?:["\',\s>])', source, re.I),
        "noindex_present": contains(r'<meta\s+name=["\']robots["\'][^>]*noindex', source, re.I),
        "pre_release_stage_visible": "PRE-RELEASE" in source and "tb-stage" in source,
        "specialist_validation_boundary_visible": contains(r'specialist validation', source, re.I),
        "regulatory_boundary_visible": contains(r'10\s*\^?\s*-?7|10⁻⁷|ROMER_SCREENING_HEURISTIC', source, re.I),
        "responsive_rules_present": contains(r'@media\s*\(', source, re.I),
        "aria_expanded_present": "aria-expanded" in source,
        "aria_pressed_present": "aria-pressed" in source,
        "controlled_snapshot_contract_present": "CONTROLLED_WORKBOOK_SNAPSHOT" in source,
        "hard_surface_floor_present": contains(r'minAltitudeKm\s*[:=]\s*1\b|MIN_CAMERA_ALTITUDE_KM', source),
        "three_view_contract_present": all(token in source for token in ("globe", "object", "orbit")),
        "run_status_or_receipt_surface_present": contains(r'RunID|runId|RUN_HISTORY', source),
    }

    advisories = {
        "reduced_motion_contract_present": contains(r'prefers-reduced-motion', source, re.I),
        "focus_visible_contract_present": contains(r':focus-visible|focus-visible', source, re.I),
        "live_region_present": contains(r'aria-live', source, re.I),
        "skip_link_present": contains(r'skip-link|skip to', source, re.I),
    }

    hard_failures = [name for name, ok in hard_contracts.items() if not ok]
    advisory_gaps = [name for name, ok in advisories.items() if not ok]

    receipt = {
        "schema": "romer.mpl.ui_fidelity_static_audit",
        "source": str(path),
        "sha256": sha256,
        "evidence_class": "SOURCE_UI_CONTRACT",
        "hard_contracts": hard_contracts,
        "hard_failures": hard_failures,
        "advisories": advisories,
        "advisory_gaps": advisory_gaps,
        "release_gate": "FAIL" if hard_failures else ("PASS_WITH_ADVISORIES" if advisory_gaps else "PASS"),
        "boundaries": [
            "STATIC_UI_PASS != BROWSER_PROVIDER_READBACK",
            "CI_PASS != EMPIRICAL_VALIDATION",
            "UI_FIDELITY != SCIENTIFIC_FIDELITY",
            "PRE_RELEASE != PUBLICLY_RELEASED",
        ],
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 1 if hard_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
