from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from mpl_static_audit import audit_source, duplicate_html_ids, summary


def ids(source: str) -> set[str]:
    return {finding.finding_id for finding in audit_source(source)}


BASE = """
<meta name="robots" content="noindex">
<script>
const MPL_SHEET_ID='sheet-fixture';
const DRIVE_FOLDER='folder-fixture';
const APPS_SCRIPT='https://script.google.com/macros/s/fixture/exec';
function calculateMPL(x){return x}
</script>
"""


class MPLStaticAuditTests(unittest.TestCase):
    def test_base_does_not_fail_locked_ids_or_calc_count(self):
        found = ids(BASE)
        self.assertNotIn("MPL-SRC-001", found)
        self.assertNotIn("MPL-SRC-002", found)
        self.assertNotIn("MPL-SRC-003", found)
        self.assertNotIn("MPL-CODE-001", found)

    def test_conflicting_years(self):
        found = ids(BASE + "\n// ASA MPL CONSTANTS — AUD 2024\n// MPL ENGINE — ASA 2019")
        self.assertIn("MPL-REG-001", found)

    def test_hardcoded_probability(self):
        found = ids(BASE + "\ndocument.getElementById('iip-prob').textContent = '< 1×10⁻⁷';")
        self.assertIn("MPL-CLAIM-002", found)

    def test_iip_screening_detected(self):
        found = ids(BASE + "\nconst dist = simData.alt * 2.8;")
        self.assertIn("MPL-MODEL-001", found)

    def test_risk_shape_mismatch(self):
        found = ids(BASE + "\nriskHeatPoints.push({risk:ZONES[x]}); if(latest.zone==='URBAN'){}")
        self.assertIn("MPL-BUG-001", found)

    def test_fss_boundary_bug(self):
        found = ids(BASE + "\nfssEl.textContent=timeToFail > 30 ? 'NOMINAL' : timeToFail > 5 ? 'CAUTION' : 'NOMINAL';")
        self.assertIn("MPL-BUG-002", found)

    def test_opaque_webhook_success(self):
        found = ids(BASE + "\nfetch(url,{mode:'no-cors'}); toast('✓ Webhook dispatched');")
        self.assertIn("MPL-SEC-001", found)

    def test_arbitrary_http_webhook(self):
        found = ids(BASE + "\nconst webhookUrl=S.webhookUrl||''; if(webhookUrl.startsWith('http')) fetch(webhookUrl);")
        self.assertIn("MPL-SEC-002", found)

    def test_inner_html_review(self):
        found = ids(BASE + "\nel.innerHTML = `<b>${name}</b>`;")
        self.assertIn("MPL-SEC-003", found)

    def test_duplicate_ids(self):
        self.assertEqual(duplicate_html_ids('<div id="a"></div><span id="a"></span>'), ["a"])

    def test_duplicate_calculation_definition(self):
        found = ids(BASE + "\nfunction calculateMPL(y){return y}")
        self.assertIn("MPL-CODE-001", found)

    def test_release_summary_blocks_high_fail(self):
        findings = audit_source(BASE + "\nconst dist=simData.alt * 2.8;")
        self.assertEqual(summary(findings)["release_gate"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
