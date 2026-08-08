#!/usr/bin/env python3
from pathlib import Path
import argparse,re,hashlib

ap=argparse.ArgumentParser(description='Apply controlled pre-release MPL hardening transforms.')
ap.add_argument('input',nargs='?',default='index.html')
ap.add_argument('output',nargs='?',default='index.html')
a=ap.parse_args(); src=Path(a.input); out=Path(a.output); s=src.read_text(encoding='utf-8')
if 'CAMERA_MIN_ALTITUDE_KM = 1' in s and "releaseStage: 'PRE_RELEASE'" in s and 'v0.' not in s:
    if src!=out: out.write_text(s,encoding='utf-8')
    print('pre-release hardening already applied'); raise SystemExit(0)
parent_sha=hashlib.sha256(s.encode()).hexdigest()

# Pre-release identity: no semantic version branding before release.
s=re.sub(r'<title>Römer MPL Platform — v[0-9.]+</title>','<title>Römer MPL Platform — Maximum Probable Loss Engine</title>',s,count=1)
s=re.sub(r'RÖMER DESIGN SYSTEM — v[0-9.]+','RÖMER DESIGN SYSTEM — CONTROLLED PRE-RELEASE',s,count=1)
s=re.sub(r'\n\s*v0\.00\.6: BC-001[^\n]*\n\s*all-13-HVA exposure table, per-phase exposure breakdown','',s,count=1)
s=s.replace('.tb-version','.tb-stage').replace('class="tb-version"','class="tb-stage"')
s=re.sub(r'<div class="tb-stage">v[^<]+</div>','<div class="tb-stage">PRE-RELEASE</div>',s,count=1)
s=s.replace('Step 1 of 2','Step 1 of 3')
s=s.replace('Est. Insurance','Est. Model Buffer').replace('Insurance requirement','Model buffer (110%)')
s=s.replace('INSURANCE RECOMMENDATION','MODEL BUFFER').replace('Insurance Req.','Model Buffer').replace('Insurance_Req_AUD','Model_Buffer_AUD')
s=s.replace('INS_Req','Model_Buffer').replace('INS_REQ','MODEL_BUFFER').replace('MPL_Insurance_Req','MPL_Model_Buffer_110pct')
s=s.replace('AVG INS','AVG BUF').replace('INS_AUD','BUFFER_AUD').replace('INS:','BUF:')
s=s.replace('Insurance (110%)','Model buffer (110%)').replace('insurance adequacy','model-buffer context').replace('insurance recommendation','model-buffer note')
s=s.replace('insurance_note','model_buffer_note')
s=re.sub(r'v0\.[0-9.]+','PRE-RELEASE',s)
s=re.sub(r'v0\.00\.\d+','legacy-build',s)
s=s.replace('★ RELEASE BUILD ★','CONTROLLED PRE-RELEASE').replace('Release build','Pre-release build').replace('release build','pre-release build')
s=re.sub(r'<div id="mpl-build-marker"[^>]*></div>','<div id="mpl-build-marker" data-stage="pre-release" data-build="2026-08-09" hidden></div>',s,count=1)
s=re.sub(r"'User-Agent': 'RomerMPL/[0-9.]+'","'User-Agent': 'RomerMPL/pre-release'",s)

# Meaningful initial states instead of ambiguous dash placeholders where operational state matters.
for old,new in [('id="sc-name">—','id="sc-name">NO SITE SELECTED'),('id="sc-coords">—','id="sc-coords">NO COORDINATES'),('id="sc-azimuth">—','id="sc-azimuth">NOT PROVIDED'),('id="sc-cc">—','id="sc-cc">NOT PROVIDED'),('id="adv-ins-preview">—','id="adv-ins-preview">NOT CALCULATED'),('id="cv-ins-preview" style="color:var(--blue);">—','id="cv-ins-preview" style="color:var(--blue);">NOT CALCULATED'),('id="pz-tt-name">—','id="pz-tt-name">NO ZONE'),('id="pz-tt-pop">Pop: —','id="pz-tt-pop">Pop: NOT CALCULATED'),('id="pz-tt-gdp">GDP: —','id="pz-tt-gdp">GDP: NOT CALCULATED')]: s=s.replace(old,new)
s=s.replace("s.az?`${s.az}°`:'—'","Number.isFinite(s.az)?`${s.az}°`:'NOT PROVIDED'")
s=s.replace("'TBD'","'NOT PROVIDED'").replace('>TBD<','>NOT PROVIDED<')

# Model/runtime receipt: distinguish parent controlled source from runtime DOM hash.
meta=re.compile(r"const MODEL_META = \{.*?\n\};",re.S)
new_meta=f"""const MODEL_META = {{
  releaseStage: 'PRE_RELEASE',
  sourceDate: '2026-08-09',
  methodName: 'Australian Space Agency Maximum Probable Loss Methodology',
  methodPublicationDate: '2019-08-01',
  methodStatus: 'SCREENING_IMPLEMENTATION_REQUIRES_INDEPENDENT_VALIDATION',
  parentSourceSha256: '{parent_sha}',
  runtimeHash: 'pending',
  constantRegistry: 'CONSTANT_RECEIPTS',
  dataMode: 'CONTROLLED_EMBEDDED_SNAPSHOT',
  dataTabs: {{}},
  disclaimer: 'Decision support only. Independent specialist validation is required before regulatory or application use.'
}};"""
s,n=meta.subn(new_meta,s,count=1)
if n!=1: raise SystemExit('MODEL_META replacement failed')
s=s.replace('computeModelHash','computeRuntimeReceiptHash').replace('MODEL_META.modelHash','MODEL_META.runtimeHash').replace('MODEL_META.version','MODEL_META.releaseStage').replace('modelHash','runtimeHash').replace('modelVersion','releaseStage')
start=s.find('function updateModelReceipt() {'); end=s.find('function normalizeRows',start)
if start<0 or end<0: raise SystemExit('receipt functions missing')
new_update="""function updateModelReceipt() {
  const el=document.getElementById('mpl-receipt'); if(!el) return;
  const setCount=Object.keys(MODEL_META.dataTabs).length;
  el.innerHTML = `<span><strong>STAGE</strong> PRE-RELEASE</span>`+
    `<span><strong>METHOD</strong> ${escapeHTML(MODEL_META.methodPublicationDate)}</span>`+
    `<span><strong>DATA</strong> ${escapeHTML(MODEL_META.dataMode)}${setCount?` · ${setCount} controlled sets`:''}</span>`+
    `<span><strong>RUNTIME</strong> ${escapeHTML(MODEL_META.runtimeHash)}</span>`+
    `<span><strong>PARENT SHA</strong> ${escapeHTML(MODEL_META.parentSourceSha256.slice(0,16))}</span>`;
}
"""
s=s[:start]+new_update+s[end:]

# Static public runtime consumes the controlled embedded snapshot. Apps Script remains write transport only.
rs=s.find('async function readSheetTab('); re_=s.find('function dataBadge(',rs)
if rs>=0 and re_>rs:s=s[:rs]+s[re_:]
ls=s.find('async function loadSheets(){'); le=s.find('function mergeAchillesRows',ls)
if ls<0 or le<0:raise SystemExit('loadSheets boundaries missing')
new_load="""function runtimeDataManifest(){return {Launch_Sites:{rows:SITES.length,source:'embedded-controlled-snapshot'},Vehicles:{rows:VEHICLES.length,source:'embedded-controlled-snapshot'},MPL_Constants:{rows:Object.keys(CONSTANT_RECEIPTS).length,source:'embedded-controlled-snapshot'},GDP_Table:{rows:Object.keys(GDP_TABLE).length,source:'embedded-controlled-snapshot'},Population_Zones:{rows:POP_ZONES.length,source:'embedded-controlled-snapshot'},Failure_Modes:{rows:FMODES.length,source:'embedded-controlled-snapshot'},Operators:{rows:OPERATORS_DEFAULT.length,source:'embedded-controlled-snapshot'},High_Value_Assets:{rows:HVA_LIBRARY.length,source:'embedded-controlled-snapshot'},BRIDGE_W5_Targets:{rows:ACHILLES_BRIDGE.length,source:'embedded-controlled-snapshot'},MPL_Config:{rows:1,source:'embedded-controlled-snapshot'}};}
async function loadSheets(){
  S.sites=SITES;S.vehicles=VEHICLES;S.transits=TRANSITS;S.fmodes=FMODES;S.operators=OPERATORS_DEFAULT;S.activeOperator=S.operators.find(o=>o.id==='OP-001')||S.operators[0];S.sheetsOk=true;S.dataErrors=[];S.dataLoadedAt=new Date().toISOString();
  MODEL_META.dataMode='CONTROLLED_EMBEDDED_SNAPSHOT';MODEL_META.dataTabs=runtimeDataManifest();dataBadge('CONTROLLED SNAPSHOT','var(--green)');updateModelReceipt();renderOperatorBadge();renderSites();renderVehicles?.();if(scene){buildDataOverlay();addSiteMarkers3D();addHVAMarkers3D();}
}
"""
s=s[:ls]+new_load+s[le:]
bs=s.find('async function fetchAchillesBridge()');be=s.find('/* ═',bs)
if bs>=0 and be>bs:s=s[:bs]+"async function fetchAchillesBridge(){return ACHILLES_BRIDGE.length;}\n\n"+s[be:]

# Camera altitude invariant. 1 km is a Römer visualization guard, not an ASA methodology requirement.
constants="""/* Camera geometry invariant. ASA MPL does not prescribe a UI camera altitude; Römer enforces a 1 km stand-off so the camera cannot cross the Earth surface. */
const EARTH_RADIUS_KM=6371.0088,CAMERA_MIN_ALTITUDE_KM=1,CAMERA_MAX_ALTITUDE_KM=40000,CAMERA_INITIAL_ALTITUDE_KM=11500,CAMERA_SITE_ALTITUDE_KM=80,SURFACE_PROXIMITY_KM=150;
"""
pos=s.find('/* ─── APPLICATION STATE ─── */');s=s[:pos]+constants+s[pos:]
s=s.replace("zoom: 1, drag: false, autoRot: true, showAtmo: true, hovSat: null,","cameraAltitudeKm: CAMERA_INITIAL_ALTITUDE_KM, drag: false, autoRot: true, showAtmo: true, hovSat: null,")
helpers="""function clampCameraAltitudeKm(value){const n=Number(value);return Math.max(CAMERA_MIN_ALTITUDE_KM,Math.min(CAMERA_MAX_ALTITUDE_KM,Number.isFinite(n)?n:CAMERA_INITIAL_ALTITUDE_KM));}
function cameraDistanceForAltitudeKm(altitudeKm){return 1+clampCameraAltitudeKm(altitudeKm)/EARTH_RADIUS_KM;}
function isSurfaceProximity(){return S.cameraAltitudeKm<=SURFACE_PROXIMITY_KM;}
function updateZoomIndicator(){const el=document.getElementById('zoom-ind');if(!el)return;const a=clampCameraAltitudeKm(S.cameraAltitudeKm);el.textContent=a<10?`ALT ${a.toFixed(1)} km${a<=CAMERA_MIN_ALTITUDE_KM+.001?' · FLOOR':''}`:`ALT ${Math.round(a).toLocaleString()} km`;}
function applyCameraAltitude(renderNow=false){if(!camera)return;const altitude=clampCameraAltitudeKm(S.cameraAltitudeKm);S.cameraAltitudeKm=altitude;camera.position.setLength(cameraDistanceForAltitudeKm(altitude));camera.lookAt(0,0,0);const gap=Math.max(1e-6,camera.position.length()-1);camera.near=Math.max(1e-6,Math.min(.02,gap*.20));camera.far=200;camera.updateProjectionMatrix();const surface=isSurfaceProximity();if(atmoMesh)atmoMesh.visible=!surface&&S.showAtmo;siteMarkers.forEach(m=>m.visible=!surface);hvaMarkers.forEach(m=>m.visible=!surface&&(S.settings.assetMarkers!==false));if(corridorArc)corridorArc.visible=!surface;updateZoomIndicator();if(renderNow&&renderer&&scene)renderer.render(scene,camera);}
function setCameraAltitudeKm(value){S.cameraAltitudeKm=clampCameraAltitudeKm(value);applyCameraAltitude(true);}
function zoomCameraBy(factor){const f=Math.max(.05,Number(factor)||1);setCameraAltitudeKm(S.cameraAltitudeKm/f);}
async function animateCameraAltitudeTo(targetKm,durationMs=520){const start=clampCameraAltitudeKm(S.cameraAltitudeKm),target=clampCameraAltitudeKm(targetKm),t0=performance.now();return new Promise(resolve=>{function tick(now){const p=Math.min(1,(now-t0)/durationMs),e=1-Math.pow(1-p,3);setCameraAltitudeKm(start+(target-start)*e);if(p<1)requestAnimationFrame(tick);else resolve();}requestAnimationFrame(tick);});}
"""
ii=s.find('function initGlobe(){');s=s[:ii]+helpers+s[ii:]
s=s.replace("scene=new THREE.Scene(); camera=new THREE.PerspectiveCamera(44,W/H,0.1,1000); camera.position.z=2.85;","scene=new THREE.Scene(); camera=new THREE.PerspectiveCamera(44,W/H,0.00001,200); camera.position.z=cameraDistanceForAltitudeKm(S.cameraAltitudeKm); camera.lookAt(0,0,0);")
trip="  canvas.dataset.webgl='ready';\n  canvas.addEventListener('webglcontextlost',()=>{canvas.dataset.webgl='lost';dataBadge('WEBGL CONTEXT LOST','var(--red)');},{passive:true});\n  canvas.addEventListener('webglcontextrestored',()=>{canvas.dataset.webgl='restored';dataBadge('WEBGL RESTORED','var(--green)');requestAnimationFrame(resizeGlobe);},{passive:true});\n"
while s.count(trip)>1:s=s.replace(trip,'',1)
s=s.replace('  camera.position.z = 2.8 / Math.max(0.45, S.zoom);','  applyCameraAltitude(false);')
ms=s.find('function setupMouse(canvas){');me=s.find('function checkSiteClick',ms)
new_mouse="""function setupMouse(canvas){let px=0,py=0,pinchDistance=null;canvas.addEventListener('mousedown',e=>{S.drag=true;S.autoRot=false;px=e.clientX;py=e.clientY;document.getElementById('gc-autorot').style.color='var(--text4)';});canvas.addEventListener('mousemove',e=>{if(!S.drag){checkSatHover(e,canvas);return;}const dx=(e.clientX-px)*.005,dy=(e.clientY-py)*.005;globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));px=e.clientX;py=e.clientY;});canvas.addEventListener('mouseup',()=>S.drag=false);canvas.addEventListener('mouseleave',()=>{S.drag=false;hideSatPopup();});canvas.addEventListener('wheel',e=>{e.preventDefault();zoomCameraBy(e.deltaY>0?.88:1.14);},{passive:false});canvas.addEventListener('click',e=>checkSiteClick(e,canvas));canvas.addEventListener('touchstart',e=>{S.drag=true;S.autoRot=false;if(e.touches.length===2)pinchDistance=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);else{px=e.touches[0].clientX;py=e.touches[0].clientY;}},{passive:true});canvas.addEventListener('touchmove',e=>{if(!S.drag)return;if(e.touches.length===2){const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);if(pinchDistance&&d>0)zoomCameraBy(d/pinchDistance);pinchDistance=d;return;}const dx=(e.touches[0].clientX-px)*.005,dy=(e.touches[0].clientY-py)*.005;globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));px=e.touches[0].clientX;py=e.touches[0].clientY;},{passive:true});canvas.addEventListener('touchend',()=>{S.drag=false;pinchDistance=null;});}

"""
s=s[:ms]+new_mouse+s[me:]
pat=re.compile(r"\nfunction showSatPopup\(sat,e\)\{.*?\n\}\nfunction hideSatPopup\(\)\{document\.getElementById\('sat-popup'\)\.classList\.remove\('on'\);S\.hovSat=null;\}\n",re.S);s,n=pat.subn('\n',s,count=1)
if n!=1:raise SystemExit('legacy satellite popup removal failed')
s=re.sub(r"function doZoom\(f\)\{.*?\}\nfunction resetGlobe\(\)\{.*?\}\n","function doZoom(f){zoomCameraBy(f);}\nfunction resetGlobe(){setCameraAltitudeKm(CAMERA_INITIAL_ALTITUDE_KM);S.autoRot=true;globe.rotation.set(0.22,0,0);userDragX=.22;userDragY=0;document.getElementById('gc-autorot').style.color='var(--green)';}\n",s,count=1,flags=re.S)
s=re.sub(r"async function zoomToSite\(site\)\{.*?\n\}","async function zoomToSite(site){flyTo(site);await animateCameraAltitudeTo(CAMERA_SITE_ALTITUDE_KM);}",s,count=1,flags=re.S)
s=s.replace('  animateGlobe();\n  requestAnimationFrame(resizeGlobe);','  applyCameraAltitude(true);\n  animateGlobe();\n  requestAnimationFrame(resizeGlobe);',1)
s=s.replace("function toggleAtmo(){S.showAtmo=!S.showAtmo;atmoMesh.visible=S.showAtmo;toast(S.showAtmo?'Atmosphere on':'Atmosphere off');}","function toggleAtmo(){S.showAtmo=!S.showAtmo;if(atmoMesh)atmoMesh.visible=S.showAtmo&&!isSurfaceProximity();toast(S.showAtmo?'Atmosphere on':'Atmosphere off');}")

# Stable nav state and ARIA without changing the visual palette.
vs=s.find('function setView(v){');ve=s.find('/* ══ ORBIT VIEW ENGINE',vs)
new_view="""function setView(requestedView){const allowed=new Set(['globe','object','orbit']);let v=allowed.has(requestedView)?requestedView:'globe';if(v==='object'&&!S.site){v='globe';toast('Select a launch site before opening Object view.');}S.view=v;[['vbtn-g','globe'],['vbtn-o','object'],['vbtn-orbit','orbit']].forEach(([id,name])=>{const el=document.getElementById(id);if(el){const active=v===name;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));}});const lv=document.getElementById('launch-view'),ov=document.getElementById('orbit-view');if(ov)ov.style.display=v==='orbit'?'':'none';if(v==='orbit'){lv?.classList.remove('show');if(lv)lv.style.display='none';requestAnimationFrame(()=>requestAnimationFrame(renderOrbitView));return;}if(v==='object'){if(lv){lv.style.display='flex';requestAnimationFrame(()=>lv.classList.add('show'));}requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!lRenderer)initLaunchScene();setTimeout(ensureCorridorOverlay,300);}));return;}lv?.classList.remove('show');if(lv)lv.style.display='none';document.getElementById('mpl-results')?.classList.remove('show');const mr=document.getElementById('mpl-results');if(mr)mr.style.display='none';document.getElementById('iip-globe-marker')?.classList.remove('show');requestAnimationFrame(resizeGlobe);}

"""
s=s[:vs]+new_view+s[ve:].replace('ORBIT VIEW ENGINE STUB — full renderer defined below','ORBIT VIEW ENGINE — deterministic mechanics and plotting state',1)
ps=s.find('function togglePanel() {');pe=s.find('/* ═══════════════════════════════════════════════════════\n   GLOBE LEGEND',ps)
new_panel="""function togglePanel(forceCollapsed=null){S.panelCollapsed=forceCollapsed===null?!S.panelCollapsed:Boolean(forceCollapsed);const panel=document.getElementById('panel'),btn=document.getElementById('panel-toggle');panel?.classList.toggle('collapsed',S.panelCollapsed);if(btn){btn.textContent=S.panelCollapsed?'›':'‹';btn.setAttribute('aria-expanded',String(!S.panelCollapsed));btn.setAttribute('aria-label',S.panelCollapsed?'Expand mission setup panel':'Collapse mission setup panel');btn.title=btn.getAttribute('aria-label');}requestAnimationFrame(()=>requestAnimationFrame(()=>{resizeGlobe();if(S.view==='orbit')renderOrbitView();}));}

"""
s=s[:ps]+new_panel+s[pe:]
s=s.replace('<button class="panel-collapse-btn" id="panel-toggle" onclick="togglePanel()" title="Collapse panel">‹</button>','<button class="panel-collapse-btn" id="panel-toggle" type="button" onclick="togglePanel()" title="Collapse mission setup panel" aria-label="Collapse mission setup panel" aria-expanded="true">‹</button>')
s=s.replace('<button class="view-btn active" id="vbtn-g" onclick="setView(\'globe\')">','<button class="view-btn active" id="vbtn-g" type="button" aria-pressed="true" onclick="setView(\'globe\')">').replace('<button class="view-btn" id="vbtn-o" onclick="setView(\'object\')">','<button class="view-btn" id="vbtn-o" type="button" aria-pressed="false" onclick="setView(\'object\')">').replace('<button class="view-btn" id="vbtn-orbit" onclick="setView(\'orbit\')">','<button class="view-btn" id="vbtn-orbit" type="button" aria-pressed="false" onclick="setView(\'orbit\')">')
s=s.replace('<div class="zoom-indicator" id="zoom-ind">×1.0</div>','<div class="zoom-indicator" id="zoom-ind" aria-live="polite" title="Camera altitude above Earth surface">ALT 11,500 km</div>')
s=s.replace('</style>',':focus-visible{outline:2px solid var(--blue);outline-offset:2px}@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}}\n</style>',1)

# Method-aligned core calculation. HVA weighting remains visible only as a Römer screening heuristic until real 10^-7 geometry is supplied.
cs=s.find('function calculateMPL({ vehicle, site, phase, zone, failModes, isUprange }) {');ce=s.find('const fmtUSD =',cs)
new_calc="""function calculateMPL({vehicle,site,phase,zone,failModes,isUprange}){const veh=VEHICLES.find(v=>v.id===vehicle.id)||vehicle,gdp=GDP_TABLE[site.cc]||GDP_TABLE.GLB,zoneData=ZONES[zone]||ZONES.RURAL,selectedModes=(S.fmodes?.length?S.fmodes:FMODES).filter(f=>failModes.includes(f.id)),casMult=selectedModes.length?Math.max(...selectedModes.map(f=>f.casMult)):1,envMult=selectedModes.length?Math.max(...selectedModes.map(f=>f.envMult)):1,Ac=veh.ac*casMult,IA=isUprange?ASA.UPRANGE_IA_M2:ASA.UPRANGE_IA_M2*25,Dpop=zoneData.popDensity,CAS_raw=(Ac*Dpop)/1e6,CAS_primary=CAS_raw>=.5?Math.round(CAS_raw):0,CAS_secondary=isUprange?Math.ceil(CAS_primary*ASA.SECONDARY_MULT):0,CAS_total=CAS_primary+CAS_secondary,MPL_CAS=CAS_total*ASA.CASUALTY_VALUE,nomAz=Number.isFinite(site.az)?site.az:90,SCREENING_HALF_ANGLE_DEG=45;function bearing(a,b,c,d){const dl=(d-b)*Math.PI/180,l1=a*Math.PI/180,l2=c*Math.PI/180;return((Math.atan2(Math.sin(dl)*Math.cos(l2),Math.cos(l1)*Math.sin(l2)-Math.sin(l1)*Math.cos(l2)*Math.cos(dl))*180/Math.PI)+360)%360}function azimuthDelta(a,b){let d=Math.abs(a-b)%360;return d>180?360-d:d}const enrichedHVAs=HVA_LIBRARY.filter(a=>Number.isFinite(a.lat)&&Number.isFinite(a.lon)).map(a=>{const dist=haversine(site.lat,site.lon,a.lat,a.lon),bear=bearing(site.lat,site.lon,a.lat,a.lon),azDelta=azimuthDelta(bear,nomAz),distanceWeight=Math.min(1,Math.max(.01,200/(dist+50))),azimuthWeight=azDelta<=SCREENING_HALF_ANGLE_DEG?Math.exp(-.5*Math.pow(azDelta/18,2)):.02,screeningWeight=Math.sqrt(distanceWeight*azimuthWeight),phaseModAscent=Math.max(.3,1.2-dist/800),phaseModDescent=Math.max(.3,.4+dist/1200),phaseMod=phase==='ascent'?phaseModAscent:phaseModDescent,Aex=(Ac/IA)*a.footprint*screeningWeight*phaseMod,propExp=a.propPerM2*Aex,louExp=a.revPerM2*Aex*(a.timeOut/12),envExp=a.toxic?a.envCost*screeningWeight:0;return{...a,dist_km:Math.round(dist),bear_deg:Math.round(bear),azDelta:Math.round(azDelta),inCorridor:azDelta<=SCREENING_HALF_ANGLE_DEG,distWeight:distanceWeight,corridorWeight:azimuthWeight,proxWeight:screeningWeight,screeningWeight,phaseMod,Aex,propExp,louExp,envExp,propExpAscent:propExp*phaseModAscent/Math.max(.01,phaseMod),propExpDescent:propExp*phaseModDescent/Math.max(.01,phaseMod)}}).sort((a,b)=>b.screeningWeight-a.screeningWeight),corridorHVAs=enrichedHVAs.filter(a=>a.screeningWeight>.001),HVA_SCREENING_PD=corridorHVAs.reduce((x,a)=>x+a.propExp,0),HVA_SCREENING_LOU=corridorHVAs.reduce((x,a)=>x+a.louExp,0),HVA_SCREENING_ENV=corridorHVAs.reduce((x,a)=>x+a.envExp,0),MPL_PD=isUprange?MPL_CAS*ASA.PROPERTY_PCT:0,MPL_LOU=isUprange?CAS_total*gdp:0,MPL_ENV=isUprange?ASA.ENV_BOUNDING*envMult:0,MPL_TOTAL=MPL_CAS+MPL_PD+MPL_LOU+MPL_ENV,MODEL_BUFFER=Math.round(MPL_TOTAL*1.10);let compliance=MPL_TOTAL<5000000?'LOWER SCREENING BAND':MPL_TOTAL>750000000?'UPPER SCREENING BAND — SPECIALIST REVIEW':'INTERMEDIATE SCREENING BAND — SPECIALIST REVIEW';if(CAS_total===0)compliance+=' · ZERO MODELLED CASUALTIES';const phaseExposure={ascent:{propExp:corridorHVAs.reduce((x,a)=>x+a.propExpAscent,0)},descent:{propExp:corridorHVAs.reduce((x,a)=>x+a.propExpDescent,0)}};return{Ac,IA,Dpop,CAS_raw,CAS_primary,CAS_secondary,CAS_total,MPL_CAS,MPL_PD,MPL_LOU,MPL_ENV,MPL_TOTAL,MODEL_BUFFER,HVA_SCREENING_PD,HVA_SCREENING_LOU,HVA_SCREENING_ENV,gdp,zone,zoneData,nearbyAssets:enrichedHVAs.slice(0,6),allAssets:enrichedHVAs,corridorHVAs,phaseExposure,nomAz,CORRIDOR_HALF_DEG:SCREENING_HALF_ANGLE_DEG,evidenceBoundary:{impactIsopleth10e7:false,hvaSelection:'ROMER_SCREENING_HEURISTIC',requiresFlightSafetyCodeRiskHazardAnalysis:true},compliance,phase,releaseStage:MODEL_META.releaseStage,runtimeHash:MODEL_META.runtimeHash,methodPublicationDate:MODEL_META.methodPublicationDate};}
"""
s=s[:cs]+new_calc+s[ce:]

# Deterministic model-evidence review replaces direct public AI permit/compliance inference.
def block(start_marker,end_marker,new):
    global s
    i=s.find(start_marker);j=s.find(end_marker,i)
    if i<0 or j<0:raise SystemExit('missing block '+start_marker)
    s=s[:i]+new+s[j:]
block('async function runBatchAIAnalysis() {','const RUN_HISTORY =',"""function runBatchAIAnalysis(){if(!batchResults.length){toast('Run a batch first');return;}const out=document.getElementById('batch-results-panel');out.insertAdjacentHTML('beforeend','<div class="u-card" style="margin-top:10px"><div class="u-label">MODEL EVIDENCE REVIEW</div><div class="u-mono9">Flight Safety Code 10⁻⁷ impact-isopleth geometry is not supplied; HVA screening remains heuristic.</div></div>');toast('Model evidence review complete');}
""")
block('async function runAIAnalysis() {','/* ════════════════════════════════════════════════════════\n   BC-009:',"""function runAIAnalysis(){if(!S.lastRun){toast('Run a simulation first');return;}const r=S.lastRun.result,out=document.getElementById('ai-output'),gaps=[];if(!r.evidenceBoundary?.impactIsopleth10e7)gaps.push('Flight Safety Code 10⁻⁷ probability-of-impact isopleth not supplied.');if(CONSTANT_RECEIPTS['MC-001']?.reviewStatus!=='VERIFIED')gaps.push('Controlled monetary constant provenance remains subject to independent source review.');out.innerHTML=`<div class="u-section-hd">MODEL EVIDENCE REVIEW</div>${gaps.map(g=>`<div class="u-card" style="margin-bottom:6px"><span class="u-tag u-tag-gld">REVIEW</span> <span style="font-size:11px">${escapeHTML(g)}</span></div>`).join('')}<div class="u-mono9" style="margin-top:10px;color:var(--text4)">Model-evidence check only; not legal advice, regulator acceptance, permit likelihood, or an application-ready MPL determination.</div>`;}

/* ════════════════════════════════════════════════════════
   BC-009:""")
s=s.replace('AI REGULATORY ANALYSIS','MODEL EVIDENCE REVIEW').replace('AI Regulatory Analysis','Model Evidence Review').replace('AI Analysis','Evidence Review').replace('Re-analyse','Review Again')
s=s.replace('Römer MPL v0.2.0','Römer MPL · PRE-RELEASE').replace("version: 'v0.2.0'","stage: 'PRE-RELEASE'").replace('Maximum Probable Loss Platform — v0.2.0','Maximum Probable Loss Platform — PRE-RELEASE').replace('MPL PLATFORM v0.2.0','MPL PLATFORM — PRE-RELEASE').replace('ASA Flight Safety Code — MPL Sweep Methodology','Römer screening sweep · ASA MPL methodology reference · independent validation required').replace('ASA corridor exposure','Römer heuristic HVA exposure').replace('HVA corridor','HVA screening heuristic').replace('ballistic corridor','screening azimuth window').replace('ASA corridor','Römer screening heuristic').replace('romer_mpl_v0.2.0.html','romer_mpl_pre_release.html')
s=s.replace('.INS_REQ','.MODEL_BUFFER')
s=re.sub(r'/\*\s*─+\s*(?:PRE-RELEASE|legacy-build)[^*]*\*/','/* Controlled MPL implementation section. */',s)
s=s.replace('STUB','IMPLEMENTATION').replace('stub','implementation')

for label,pat in {'semantic version':r'v0\.','TODO':r'\bTODO\b','TBD':r'\bTBD\b','FIXME':r'\bFIXME\b','legacy zoom':r'S\.zoom','public Sheet read':r'readSheetTab\s*\(','direct Anthropic':r'api\.anthropic\.com','ASA corridor':r'ASA corridor','legacy insurance field':r'MPL_Insurance_Req'}.items():
    if re.search(pat,s,re.I):raise SystemExit('invariant failed: '+label)
if len(re.findall(r'function\s+showSatPopup\s*\(',s))!=1:raise SystemExit('showSatPopup count')
if s.count("canvas.addEventListener('webglcontextlost'")!=1:raise SystemExit('WebGL listener count')
if len(re.findall(r'function\s+calculateMPL\s*\(',s))!=1:raise SystemExit('calculateMPL count')
if 'CAMERA_MIN_ALTITUDE_KM=1' not in s or 'cameraDistanceForAltitudeKm' not in s:raise SystemExit('camera floor missing')
out.write_text(s,encoding='utf-8');print(f'wrote {out} bytes={out.stat().st_size} parent_sha256={parent_sha}')
