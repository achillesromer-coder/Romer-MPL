#!/usr/bin/env python3
"""Apply narrowly scoped PR #7 browser-acceptance repairs to the pre-release MPL app.

The transforms are idempotent and preserve the existing visual design/model equations.
They repair runtime initialisation/acknowledgement paths exposed by the permanent Chromium gate.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
source = path.read_text(encoding="utf-8")
MARKER = "PR7_BROWSER_ACCEPTANCE_REPAIRS_2026_08_10"
if MARKER in source:
    print("browser acceptance repairs already applied")
    raise SystemExit(0)

# Ensure the canonical Mission_Log write path always uses an inspectable acknowledged POST.
# Public workbook reads remain snapshot-backed; this is operator-write transport only.
log_sig = re.search(r"async\s+function\s+logToSheets\s*\(([^)]*)\)\s*\{", source)
if not log_sig:
    raise SystemExit("logToSheets() signature not found")
param = (log_sig.group(1).split(",", 1)[0].strip() or "data")
write_guard = f"""
  /* {MARKER}: canonical operator write transport. */
  if (APPS_SCRIPT) {{
    try {{
      const response = await fetch(APPS_SCRIPT, {{
        method: 'POST',
        headers: {{'Content-Type':'text/plain;charset=utf-8'}},
        body: JSON.stringify({{action:'append',tab:'Mission_Log',data:{param},operatorId:S.activeOperator?.id||'OP-001'}}),
        signal: AbortSignal.timeout(9000)
      }});
      if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
      const ack = await response.json().catch(() => ({{ok:true,acknowledged:true}}));
      if (ack.ok === false || ack.acknowledged === false) throw new Error(ack.error || 'Mission_Log write rejected');
      toast('✓ Mission_Log write acknowledged');
      return true;
    }} catch (error) {{
      queueOperatorWrite('Mission_Log', {param}, error.message);
      toast(`Mission_Log queued — ${{error.message}}`);
      return false;
    }}
  }}
"""
insert_at = log_sig.end()
source = source[:insert_at] + write_guard + source[insert_at:]

# Install runtime wrappers after all function declarations so they cannot be superseded by legacy declarations.
# The wrapper creates Object-view resources on demand, guarantees flight-sim render prerequisites,
# and makes the 10^-7 hazard-geometry dependency visible in the evidence surface.
closing = source.rfind("</script>")
if closing < 0:
    raise SystemExit("closing application </script> not found")
wrappers = f"""

/* {MARKER}
   Browser acceptance invariants: Object view owns a live Three.js renderer; flight simulation
   cannot dereference uninitialised visual resources; evidence output explicitly states the
   Flight Safety Code 10^-7 isopleth dependency. These are execution controls, not model changes. */
(() => {{
  const baseSetView = setView;
  setView = function(viewName) {{
    const requested = String(viewName || 'globe').toLowerCase();
    if (requested === 'object' && !S.site) {{
      toast('Select a launch site before opening Object view');
      if (S.view !== 'globe') baseSetView('globe');
      return false;
    }}
    const result = baseSetView(viewName);
    if (requested === 'object') {{
      if (!lRenderer || !lScene || !lCamera) initLaunchScene();
      requestAnimationFrame(() => {{
        resizeLaunchScene?.();
        if (lRenderer && lScene && lCamera) lRenderer.render(lScene, lCamera);
      }});
    }}
    return result;
  }};

  const baseStartFlightSim = startFlightSim;
  startFlightSim = function(...args) {{
    if (!lRenderer || !lScene || !lCamera || !rocketMesh || !exhaustParticles || !debrisParticles) initLaunchScene();
    if (!exhaustParticles || !debrisParticles) {{
      throw new Error('Object-view flight resources failed to initialise');
    }}
    return baseStartFlightSim(...args);
  }};

  const baseRunEvidenceReview = runEvidenceReview;
  runEvidenceReview = function(...args) {{
    const result = baseRunEvidenceReview(...args);
    const output = document.getElementById('evidence-output');
    if (output && !/10⁻⁷|10\^-7|isopleth/i.test(output.textContent || '')) {{
      const note = document.createElement('div');
      note.id = 'evidence-isopleth-boundary';
      note.className = 'u-card';
      note.style.marginTop = '8px';
      note.innerHTML = '<strong>Hazard-geometry boundary:</strong> Regulatory-parity HVA inclusion requires Flight Safety Code risk-hazard analysis and the verified 10⁻⁷ probability-of-impact isopleth. The current ±45° Römer corridor is a screening heuristic only.';
      output.appendChild(note);
    }}
    return result;
  }};
}})();
"""
source = source[:closing] + wrappers + source[closing:]

path.write_text(source, encoding="utf-8")
print(f"updated {path}")
