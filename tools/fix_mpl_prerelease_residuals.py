#!/usr/bin/env python3
from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')
# Idempotent residual repairs found by post-transform soft-break audit.
s=s.replace('MODEL_META.baseBlob.slice(0,16)','MODEL_META.parentSourceSha256.slice(0,16)')
s=s.replace('ins:Math.round(mplT*1.1)','buffer:Math.round(mplT*1.1)')
s=s.replace('INSURANCE REQ.','MODEL BUFFER')
s=s.replace('// Insurance recommendation row (add if element exists)','// Model buffer row (110% operational margin; not an insurance determination).')
s=s.replace('// Full HVA exposure table — all assets (PRE-RELEASE: show all 13, corridor flag, azimuth delta)','// Full HVA screening table — all controlled assets with heuristic azimuth/distance evidence.')
s=s.replace('// PRE-RELEASE corridor header','// Screening-heuristic table header.')
s=s.replace('BC-009:/* ════════════════════════════════════════════════════════\n   BC-009:', 'BC-009: MISSION URL SHARE')
s=s.replace("    ins:  Math.round(r.MODEL_BUFFER),","    buf:  Math.round(r.MODEL_BUFFER),")
s=s.replace("const ins   = +params.get('ins');","const buffer = +(params.get('buf')||params.get('ins')||0);")
# Internal variable IDs are retained where DOM compatibility matters; user-visible labels use Model Buffer.
s=s.replace('Insurance recommendation','Model buffer').replace('insurance recommendation','model buffer')
# Explicitly remove version/build data attributes if a stale transform source leaves them behind.
s=re.sub(r'\sdata-version="[^"]*"','',s)
# Hard failures for known soft-break signatures.
for label,pat in {'stale MODEL_META fallback':r'MODEL_META\.baseBlob','sweep insurance key':r'ins:Math\.round\(mplT','malformed section marker':r'BC-009:/\*','direct AI transport':r'api\.anthropic\.com','legacy camera':r'S\.zoom'}.items():
    if re.search(pat,s): raise SystemExit(f'residual invariant failed: {label}')
p.write_text(s,encoding='utf-8')
print('residual pre-release repairs applied')
