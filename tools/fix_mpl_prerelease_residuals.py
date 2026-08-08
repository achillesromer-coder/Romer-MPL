#!/usr/bin/env python3
from pathlib import Path
import re,sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')

# Idempotent residual repairs found by source, calculation and browser-path audit.
s=s.replace('MODEL_META.baseBlob.slice(0,16)','MODEL_META.parentSourceSha256.slice(0,16)')

# Model Buffer is an analytical 110% margin, not an insurance determination.
s=re.sub(r'\bins\s*:', 'buffer:', s)
s=re.sub(r'\.ins\b', '.buffer', s)
s=s.replace('avgIns','avgBuffer').replace('AVG INS','AVG BUF')
s=s.replace('Insurance_Req_AUD','Model_Buffer_AUD').replace('INS_Req','Model_Buffer').replace('INS_REQ','MODEL_BUFFER')
s=s.replace('INS. REQ.','MODEL BUFFER').replace('INSURANCE REQ.','MODEL BUFFER')
s=s.replace('Insurance Req.','Model Buffer').replace('Insurance requirement','Model buffer (110%)')
s=s.replace('Insurance recommendation','Model buffer').replace('insurance recommendation','model buffer')
s=s.replace('Est. Insurance','Est. Model Buffer')
s=s.replace('// Insurance recommendation row (add if element exists)','// Model buffer row (110% analytical margin; not an insurance determination).')

# Human-readable model comments describe current evidence rather than historical implementation state.
s=s.replace('// Full HVA exposure table — all assets (PRE-RELEASE: show all 13, corridor flag, azimuth delta)','// Full HVA screening table — all controlled assets with heuristic azimuth/distance evidence.')
s=s.replace('// PRE-RELEASE corridor header','// Screening-heuristic table header.')
s=s.replace('BC-009: MISSION URL SHARE MISSION URL SHARE','BC-009: MISSION URL SHARE')
s=s.replace('BC-009:/* ════════════════════════════════════════════════════════\n   BC-009:', 'BC-009: MISSION URL SHARE')

# Pre-release current workbook names are canonical. Legacy names remain only in TAB_ALIASES for import compatibility.
s=s.replace("tab:'09_BRIDGE_W5_Targets'","tab:'BRIDGE_W5_Targets'")
s=s.replace("tab:'10_Mission_Log'","tab:'Mission_Log'")
s=s.replace('Schema matches 10_Mission_Log tab exactly','Schema matches canonical Mission_Log tab')
s=s.replace('bridge (09_BRIDGE_W5_Targets tab)','bridge (BRIDGE_W5_Targets tab)')
s=s.replace('from 09_BRIDGE_W5_Targets','from BRIDGE_W5_Targets').replace('— 09_BRIDGE_W5_Targets','— BRIDGE_W5_Targets')
s=s.replace('Configure via CF-022 in 00_MPL_Config sheet','Configure via CF-022 in MPL_Config')
s=s.replace('Add operators via 08_Operators in MPL Engine Sheet','Add operators via Operators in the MPL Engine workbook')
s=s.replace('EMBEDDED OPERATOR PROFILES (08_Operators — OP-001/002/004)','EMBEDDED OPERATOR PROFILES (Operators — OP-001/002/004)')

# Sweep and batch keys/exports use one property name end-to-end.
s=s.replace("const headers = ['Scenario','Casualties','MPL_Total_AUD','Model_Buffer_AUD','Phase','Zone'];", "const headers = ['Scenario','Casualties','MPL_Total_AUD','Model_Buffer_AUD','Phase','Zone'];")
s=s.replace("const avgBuffer=Math.round(batchResults.reduce((s,r)=>s+r.buffer,0)/batchResults.length);", "const avgBuffer=Math.round(batchResults.reduce((s,r)=>s+r.buffer,0)/batchResults.length);")
s=s.replace("MPL_Total:r.mpl, Model_Buffer:r.buffer,", "MPL_Total:r.mpl, Model_Buffer:r.buffer,")

# The transformed run path uses await for site-focus and view transitions; it must remain async.
s=s.replace('async async function runMission(){','async function runMission(){')
if 'await zoomToSite(S.site);' in s and 'async function runMission(){' not in s:
    s=s.replace('function runMission(){','async function runMission(){',1)

# Restore the full pre-release boot/reveal sequence if a previous transform reduced it to a bootApp alias.
boot_alias="async function runSplash(){ return bootApp(); }\nwindow.addEventListener('load',runSplash);"
if boot_alias in s:
    full_boot="""const SPLASH_STEPS=[{id:'li0',t:0},{id:'li1',t:500},{id:'li2',t:1050},{id:'li3',t:1650},{id:'li4',t:2200},{id:'li5',t:2750}];
async function runSplash(){
  let revealed=false;
  const reveal=()=>{
    if(revealed)return;revealed=true;
    document.getElementById('splash')?.classList.add('out');
    document.getElementById('app')?.classList.add('live');
    if(window.matchMedia?.('(max-width:760px)').matches&&!S.panelCollapsed)setTimeout(()=>togglePanel(true),180);
    setTimeout(()=>{const splash=document.getElementById('splash');if(splash)splash.style.display='none';},1100);
    startClock();setupKeyboard();
  };
  const emergency=setTimeout(()=>{console.warn('[MPL boot] emergency reveal');try{bootApp();}catch{}reveal();},12000);
  try{
    for(let i=0;i<SPLASH_STEPS.length;i++){
      await wait(i===0?120:SPLASH_STEPS[i].t-SPLASH_STEPS[i-1].t);
      if(i>0){const prev=document.getElementById(SPLASH_STEPS[i-1].id);prev?.classList.remove('active');prev?.classList.add('done');}
      document.getElementById(SPLASH_STEPS[i].id)?.classList.add('active');
      const progress=document.getElementById('progress');if(progress)progress.style.width=((i+1)/SPLASH_STEPS.length*100)+'%';
    }
    loadSettings();
    await loadSheets();
    document.getElementById(SPLASH_STEPS.at(-1).id)?.classList.add('done');
    bootApp();
    await wait(180);reveal();
    setTimeout(()=>{document.getElementById('kbd-hints')?.classList.add('show');setTimeout(()=>document.getElementById('kbd-hints')?.classList.remove('show'),4000);},1200);
  }catch(error){console.error('[MPL boot] degraded mode',error);try{bootApp();}catch{}reveal();}
  finally{clearTimeout(emergency);}
}
window.addEventListener('load',runSplash);"""
    s=s.replace(boot_alias,full_boot,1)

# Explicit initial and reset states. Operational displays never use an ambiguous em-dash as a placeholder.
initial={
'id="ms-site">—':'id="ms-site">NO SITE SELECTED',
'id="ms-veh">—':'id="ms-veh">NO VEHICLE',
'id="ms-trans">—':'id="ms-trans">NO TRANSIT',
'id="ms-ac">—':'id="ms-ac">NOT CALCULATED',
'id="ms-mpl-est" style="font-size:11px;">—':'id="ms-mpl-est" style="font-size:11px;">NOT CALCULATED',
'id="pz-tt-name">—':'id="pz-tt-name">NO ZONE',
'id="pz-tt-pop">Pop: —':'id="pz-tt-pop">Pop: NOT CALCULATED',
'id="pz-tt-gdp">GDP: —':'id="pz-tt-gdp">GDP: NOT CALCULATED',
'id="iip-lat">—':'id="iip-lat">NOT CALCULATED',
'id="iip-lon">—':'id="iip-lon">NOT CALCULATED',
'id="iip-prob">—':'id="iip-prob">NOT CALCULATED',
'id="t-phase">—':'id="t-phase">STANDBY',
'id="t-vehicle">—':'id="t-vehicle">NO VEHICLE',
'id="t-iip">—':'id="t-iip">NO ACTIVE IIP',
'id="t-mpl-exp">—':'id="t-mpl-exp">NOT CALCULATED',
'id="t-sats">—':'id="t-sats">INITIALIZING',
'id="orb-status" style="color:var(--green);">NOMINAL':'id="orb-status" style="color:var(--text3);">NOT CALCULATED',
}
for old,new in initial.items():s=s.replace(old,new)
s=s.replace('>—°</span>','>NOT CALCULATED</span>').replace('>— km</span>','>NOT CALCULATED</span>').replace('>— min</span>','>NOT CALCULATED</span>').replace('>— m/s</span>','>NOT CALCULATED</span>')
s=s.replace('>—</span>','>NOT CALCULATED</span>')
s=s.replace("S.site?.short  || '—'","S.site?.short||'NO SITE SELECTED'").replace("S.vehicle?.name || '—'","S.vehicle?.name||'NO VEHICLE'").replace("S.transit?.name || '—'","S.transit?.name||'NO TRANSIT'")
s=s.replace("S.vehicle ? `${S.vehicle.ac.toLocaleString()} m²` : '—'","S.vehicle?`${S.vehicle.ac.toLocaleString()} m²`:'NOT CALCULATED'")
s=s.replace("||'—'","||'NOT PROVIDED'").replace("|| '—'","||'NOT PROVIDED'")
s=s.replace(":'—'",":'NOT PROVIDED'").replace(": '—'",": 'NOT PROVIDED'")

# Result-method labels describe controlled rules without stale hard-coded monetary values.
s=s.replace('§6.1 · $4.5M/casualty','§6.1 · controlled casualty value')
s=s.replace('§6.2 · 50% of CAS','§6.2 · controlled property rule')
s=s.replace('§6.3 · GDP × CAS','§6.3 · controlled loss-of-use rule')
s=s.replace('§6.4 · Bounding','§6.4 · controlled environment rule')

# ACHILLES bridge field name is retained for schema compatibility, but values are screening states, never regulator PASS/FAIL.
s=re.sub(r"MPL_Compliance:\s*r\.compliance\.includes\('PASS'\)\s*\?\s*'PASS'\s*:\s*\n\s*r\.compliance\.includes\('FAIL'\)\s*\?\s*'FAIL'\s*:\s*'REVIEW',",
         "MPL_Compliance: r.compliance.includes('LOWER')?'LOWER_SCREENING_BAND':r.compliance.includes('UPPER')?'UPPER_REVIEW_BAND':'REVIEW',",s)
s=s.replace("badge.textContent = r.compliance.includes('PASS') ? '✓ MPL PASS' : r.compliance.includes('FAIL') ? '✗ FAIL' : '⚠ REVIEW';",
            "badge.textContent=r.compliance.includes('LOWER')?'MPL LOWER BAND':r.compliance.includes('UPPER')?'MPL UPPER REVIEW':'MPL REVIEW';")
s=s.replace("badge.style.color = r.compliance.includes('PASS') ? 'var(--green)' : r.compliance.includes('FAIL') ? 'var(--red)' : 'var(--gold)';",
            "badge.style.color=r.compliance.includes('LOWER')?'var(--green)':r.compliance.includes('UPPER')?'var(--orange)':'var(--gold)';")

# W6 is an authenticated endpoint (anonymous browser request returns 401). Build an inspectable receipt instead of issuing a doomed browser write.
w6_start=s.find('async function writeAchillesW6(r) {')
w6_end=s.find('/* ═══════════════════════════════════════════════════════\n   MULTI-OPERATOR WEBHOOK',w6_start)
if w6_start>=0 and w6_end>w6_start:
    w6="""function writeAchillesW6(r){
  const receipt={state:'AUTH_REQUIRED',transport:'OPERATOR_SIDE',endpoint:'https://romer.industries/w6/data',runId:S.lastRun?.runId,site:S.site?.id,mplTotal:Math.round(r.MPL_TOTAL),assetExposureCount:(r.allAssets||r.nearbyAssets||[]).length,timestamp:new Date().toISOString()};
  S.lastW6Receipt=receipt;
  return receipt;
}

"""
    s=s[:w6_start]+w6+s[w6_end:]

# Pre-release settings use stage terminology, not semantic release versioning.
s=s.replace("version: 'PRE-RELEASE',","stage: 'PRE_RELEASE',")
s=s.replace("toast(`✓ Config imported — v${config.version||'?'} from ${new Date(config.exported||0).toLocaleDateString()}`);",
            "toast(`✓ Config imported — ${config.stage||config.version||'LEGACY_CONFIG'} · ${new Date(config.exported||0).toLocaleDateString()}`);")
s=s.replace("model:{version:MODEL_META.releaseStage,hash:MODEL_META.runtimeHash,methodPublicationDate:MODEL_META.methodPublicationDate}",
            "model:{stage:MODEL_META.releaseStage,runtimeHash:MODEL_META.runtimeHash,methodPublicationDate:MODEL_META.methodPublicationDate}")

# Deterministic model-evidence review replaces removed external AI/regulatory analysis transport.
s=s.replace('<span style="font-family:var(--font-mono);font-size:8px;color:var(--text4);">Powered by Claude · CF-020</span>',
            '<span style="font-family:var(--font-mono);font-size:8px;color:var(--text4);">Deterministic evidence review · no external AI call</span>')

# Run-history and batch colours describe screening bands rather than pass/fail regulatory states.
s=s.replace("const col  = comp.includes('PASS')?'var(--green)':comp.includes('FAIL')?'var(--red)':'var(--gold)';",
            "const col=comp.includes('LOWER')?'var(--green)':comp.includes('UPPER')?'var(--orange)':'var(--gold)';")
s=s.replace("const cCol=r.compliance.includes('PASS')?'var(--green)':r.compliance.includes('FAIL')?'var(--red)':'var(--gold)';",
            "const cCol=r.compliance.includes('LOWER')?'var(--green)':r.compliance.includes('UPPER')?'var(--orange)':'var(--gold)';")

# Reset/new-mission telemetry returns explicit operational state.
s=s.replace("['t-site','t-vehicle','t-phase','t-iip'].forEach(id=>document.getElementById(id).textContent='—');\n  document.getElementById('t-site').textContent='NONE';\n  document.getElementById('t-mpl-exp').textContent='—';",
            "document.getElementById('t-site').textContent='NONE';\n  document.getElementById('t-vehicle').textContent='NO VEHICLE';\n  document.getElementById('t-phase').textContent='STANDBY';\n  document.getElementById('t-iip').textContent='NO ACTIVE IIP';\n  document.getElementById('t-mpl-exp').textContent='NOT CALCULATED';")

# Explicitly remove semantic-version/build data attributes if a stale transform source leaves them behind.
s=re.sub(r'\sdata-version="[^"]*"','',s)

# Hard failures for known crash and soft-break signatures.
checks={
 'stale MODEL_META fallback':r'MODEL_META\.baseBlob',
 'insurance result property':r'\br\.ins\b|\bins\s*:',
 'malformed or duplicated share heading':r'BC-009:/\*|MISSION URL SHARE MISSION URL SHARE',
 'direct AI transport':r'api\.anthropic\.com',
 'legacy camera':r'S\.zoom',
 'double async declaration':r'async\s+async\s+function\s+runMission',
 'non-async awaited runMission':r'(?<!async\s)function\s+runMission\(\)\s*\{[\s\S]{0,1200}?await\s+zoomToSite',
 'stale visible AI provider label':r'Powered by Claude',
 'stale insurance heading':r'INSURANCE REQ\.|INS\. REQ\.',
 'legacy write tab':r"tab:'(?:09_BRIDGE_W5_Targets|10_Mission_Log)'",
}
for label,pat in checks.items():
    if re.search(pat,s):raise SystemExit(f'residual invariant failed: {label}')
if "window.addEventListener('load',runSplash);" in s and not re.search(r'async\s+function\s+runSplash\s*\(',s):
    raise SystemExit('residual invariant failed: unresolved splash boot binding')

p.write_text(s,encoding='utf-8')
print('residual pre-release repairs applied')
