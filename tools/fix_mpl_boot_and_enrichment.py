#!/usr/bin/env python3
"""Make pre-release boot deterministic and keep optional network enrichment off the critical path."""
from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')

# Shared asynchronous delay used by splash sequencing and mission view transitions.
# This is runtime infrastructure, not a placeholder timer: callers await an explicit UI transition interval.
if not re.search(r'(?:const|function)\s+wait\b',s):
    anchor='function bootApp(){'
    if anchor not in s:raise SystemExit('bootApp anchor not found')
    s=s.replace(anchor,"const wait=milliseconds=>new Promise(resolve=>setTimeout(resolve,Math.max(0,Number(milliseconds)||0)));\n\n"+anchor,1)

# Public pre-release boot is deterministic. Optional public APIs remain callable utilities but are not
# auto-started because cross-origin/browser availability is not part of the controlled runtime contract.
s=s.replace("  setTimeout(fetchLiveGDP,2500); setTimeout(fetchLivePopDensity,4200); setTimeout(fetchJPLHorizons,6200);",
            "  S.enrichmentMode='CONTROLLED_EMBEDDED_ONLY';")

# Satellite rendering starts from the embedded TLE receipt. A browser CORS proxy is not a release dependency.
s=s.replace("  fetchLiveTLEs().then(()=>{ if(satRecords.length===0) initSatelliteRecords(EMBEDDED_TLES); addSatellites3D(); });",
            "  initSatelliteRecords(EMBEDDED_TLES); addSatellites3D();")

# Natural Earth vector geometry is the controlled high-detail map layer. The NASA image loader remains an
# explicit diagnostic utility but is not called automatically because the upstream image endpoint is not CORS-safe.
s=s.replace('   L3 (~4s):       loadHDGlobeTexture() — NASA Blue Marble photorealistic HD',
            '   Optional diagnostic: loadHDGlobeTexture() — manual remote texture probe; excluded from controlled boot')
s=s.replace('    setTimeout(loadHDGlobeTexture, 200);\n    return;',
            "    if(badge){badge.textContent='PROCEDURAL MAP · CONTROLLED FALLBACK';setTimeout(()=>badge.classList.remove('show'),1800);}\n    return;")
s=s.replace("    if(badge) badge.classList.remove('show');\n    setTimeout(loadHDGlobeTexture, 200);\n    return;",
            "    if(badge){badge.textContent='PROCEDURAL MAP · VECTOR SOURCE UNAVAILABLE';setTimeout(()=>badge.classList.remove('show'),1800);}\n    return;")
s=s.replace("  if(badge){ badge.textContent='LOADING HD TEXTURE…'; }\n  const res = ctryTopo?.objects?.countries ? '50m' : '110m';\n  toast(`Vector coastlines loaded — Natural Earth ${res} · biome palette`);\n  setTimeout(loadHDGlobeTexture, 600);",
            "  const res=ctryTopo?.objects?.countries?'50m':'110m';\n  if(badge){badge.textContent=`VECTOR MAP · NATURAL EARTH ${res}`;setTimeout(()=>badge.classList.remove('show'),1600);}\n  toast(`Vector coastlines loaded — Natural Earth ${res} · biome palette`);")
s=s.replace('function loadHDGlobeTexture() {',
            "/* Manual diagnostic only: probes optional NASA/NOAA imagery without affecting controlled boot. */\nfunction loadHDGlobeTexture() {",1)

# Machine-readable boot state allows browser tests and operator diagnostics to distinguish controlled core data
# from optional enrichment availability.
s=s.replace("dataMode: 'CONTROLLED_EMBEDDED_SNAPSHOT',\n  dataTabs: {},",
            "dataMode: 'CONTROLLED_EMBEDDED_SNAPSHOT',\n  enrichmentMode: 'CONTROLLED_EMBEDDED_ONLY',\n  dataTabs: {},")
s=s.replace("S.enrichmentMode='CONTROLLED_EMBEDDED_ONLY';","S.enrichmentMode='CONTROLLED_EMBEDDED_ONLY';MODEL_META.enrichmentMode='CONTROLLED_EMBEDDED_ONLY';")

# Hard invariants: every wait call has an implementation and no optional network fetch is scheduled at boot.
if 'await wait(' in s and not re.search(r'const\s+wait\s*=',s):raise SystemExit('wait helper missing')
for forbidden in ['setTimeout(fetchLiveGDP','setTimeout(fetchLivePopDensity','setTimeout(fetchJPLHorizons','fetchLiveTLEs().then','setTimeout(loadHDGlobeTexture']:
    if forbidden in s:raise SystemExit('automatic optional enrichment remains: '+forbidden)

p.write_text(s,encoding='utf-8')
print('pre-release boot and optional enrichment boundary reconciled')
