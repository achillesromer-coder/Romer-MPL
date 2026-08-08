#!/usr/bin/env python3
from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')

# Idempotent residual repairs found by post-transform source and browser-path audit.
s=s.replace('MODEL_META.baseBlob.slice(0,16)','MODEL_META.parentSourceSha256.slice(0,16)')
s=s.replace('ins:Math.round(mplT*1.1)','buffer:Math.round(mplT*1.1)')
s=s.replace('INSURANCE REQ.','MODEL BUFFER')
s=s.replace('// Insurance recommendation row (add if element exists)','// Model buffer row (110% analytical margin; not an insurance determination).')
s=s.replace('// Full HVA exposure table — all assets (PRE-RELEASE: show all 13, corridor flag, azimuth delta)','// Full HVA screening table — all controlled assets with heuristic azimuth/distance evidence.')
s=s.replace('// PRE-RELEASE corridor header','// Screening-heuristic table header.')
s=s.replace('BC-009:/* ════════════════════════════════════════════════════════\n   BC-009:', 'BC-009: MISSION URL SHARE')
s=s.replace("    ins:  Math.round(r.MODEL_BUFFER),","    buf:  Math.round(r.MODEL_BUFFER),")
s=s.replace("const ins   = +params.get('ins');","const buffer = +(params.get('buf')||params.get('ins')||0);")
s=s.replace('${fmtUSD(r.ins)}','${fmtUSD(r.buffer)}').replace('r.ins.toLocaleString()','r.buffer.toLocaleString()')

# The transformed run path uses await for site-focus and view transitions; it must remain async.
s=s.replace('async async function runMission(){','async function runMission(){')
if 'await zoomToSite(S.site);' in s and 'async function runMission(){' not in s:
    s=s.replace('function runMission(){','async function runMission(){',1)

# Pre-release settings use a stage, not a semantic version.
s=s.replace("version: 'PRE-RELEASE',","stage: 'PRE_RELEASE',")
s=s.replace("toast(`✓ Config imported — v${config.version||'?'} from ${new Date(config.exported||0).toLocaleDateString()}`);",
            "toast(`✓ Config imported — ${config.stage||config.version||'LEGACY_CONFIG'} · ${new Date(config.exported||0).toLocaleDateString()}`);")
s=s.replace("model:{version:MODEL_META.releaseStage,hash:MODEL_META.runtimeHash,methodPublicationDate:MODEL_META.methodPublicationDate}",
            "model:{stage:MODEL_META.releaseStage,runtimeHash:MODEL_META.runtimeHash,methodPublicationDate:MODEL_META.methodPublicationDate}")

# Deterministic model-evidence review replaces the removed external AI transport.
s=s.replace('<span style="font-family:var(--font-mono);font-size:8px;color:var(--text4);">Powered by Claude · CF-020</span>',
            '<span style="font-family:var(--font-mono);font-size:8px;color:var(--text4);">Deterministic evidence review · no external AI call</span>')

# Run-history colours describe screening bands rather than pass/fail regulatory states.
s=s.replace("const col  = comp.includes('PASS')?'var(--green)':comp.includes('FAIL')?'var(--red)':'var(--gold)';",
            "const col  = comp.includes('LOWER')?'var(--green)':comp.includes('UPPER')?'var(--orange)':'var(--gold)';")

# Reset/new-mission telemetry must expose explicit operational states rather than visual placeholders.
s=s.replace("['t-site','t-vehicle','t-phase','t-iip'].forEach(id=>document.getElementById(id).textContent='—');\n  document.getElementById('t-site').textContent='NONE';\n  document.getElementById('t-mpl-exp').textContent='—';",
            "document.getElementById('t-site').textContent='NONE';\n  document.getElementById('t-vehicle').textContent='NO VEHICLE';\n  document.getElementById('t-phase').textContent='STANDBY';\n  document.getElementById('t-iip').textContent='NO ACTIVE IIP';\n  document.getElementById('t-mpl-exp').textContent='NOT CALCULATED';")

# Internal DOM IDs are retained where compatibility matters; user-visible wording uses Model Buffer.
s=s.replace('Insurance recommendation','Model buffer').replace('insurance recommendation','model buffer')
s=s.replace('Insurance Req.','Model Buffer').replace('Insurance requirement','Model buffer (110%)')

# Explicitly remove semantic-version/build data attributes if a stale transform source leaves them behind.
s=re.sub(r'\sdata-version="[^"]*"','',s)

# Hard failures for known crash and soft-break signatures.
checks={
 'stale MODEL_META fallback':r'MODEL_META\.baseBlob',
 'sweep insurance key':r'ins:Math\.round\(mplT',
 'malformed section marker':r'BC-009:/\*',
 'direct AI transport':r'api\.anthropic\.com',
 'legacy camera':r'S\.zoom',
 'double async declaration':r'async\s+async\s+function\s+runMission',
 'non-async awaited runMission':r'(?<!async\s)function\s+runMission\(\)\s*\{[\s\S]{0,1200}?await\s+zoomToSite',
 'stale visible AI provider label':r'Powered by Claude',
 'stale insurance heading':r'INSURANCE REQ\.',
}
for label,pat in checks.items():
    if re.search(pat,s): raise SystemExit(f'residual invariant failed: {label}')

p.write_text(s,encoding='utf-8')
print('residual pre-release repairs applied')
