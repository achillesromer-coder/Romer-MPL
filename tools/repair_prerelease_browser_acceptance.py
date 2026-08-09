#!/usr/bin/env python3
from pathlib import Path

# Idempotent migration: this file is safe to run repeatedly on the controlled pre-release branch.
path=Path('index.html')
source=path.read_text(encoding='utf-8')
original=source

# Satellite popup teardown is a required counterpart to hover/click presentation.
if 'function hideSatPopup()' not in source:
    anchor="  S.hovSat = userData;\n}\n\n/* ─── Globe Animation"
    replacement="  S.hovSat = userData;\n}\nfunction hideSatPopup(){\n  document.getElementById('sat-popup')?.classList.remove('on');\n  S.hovSat=null;\n}\n\n/* ─── Globe Animation"
    if anchor not in source: raise SystemExit('satellite popup anchor not found')
    source=source.replace(anchor,replacement,1)

# Popup telemetry must expose explicit state rather than an ambiguous dash.
source=source.replace("document.getElementById('sp-name').textContent = userData.name || '—';","document.getElementById('sp-name').textContent = userData.name || 'UNNAMED OBJECT';")
source=source.replace("document.getElementById('sp-alt').textContent  = r.alt  ? `${Math.round(r.alt * 6371)} km`   : '—';","document.getElementById('sp-alt').textContent  = Number.isFinite(r.alt) ? `${Math.round(r.alt * EARTH_RADIUS_KM)} km` : 'NOT CALCULATED';")
source=source.replace("document.getElementById('sp-vel').textContent  = r.vel  ? `${r.vel.toFixed(2)} km/s`           : '—';","document.getElementById('sp-vel').textContent  = Number.isFinite(r.vel) ? `${r.vel.toFixed(2)} km/s` : 'NOT CALCULATED';")
source=source.replace("? parseFloat(userData.rec.l2.slice(8,16)).toFixed(2) + '°' : '—';","? parseFloat(userData.rec.l2.slice(8,16)).toFixed(2) + '°' : 'NOT CALCULATED';")
source=source.replace("? (86400 / parseFloat(userData.rec.l2.slice(52,63))).toFixed(1) + ' min' : '—';","? (86400 / parseFloat(userData.rec.l2.slice(52,63))).toFixed(1) + ' min' : 'NOT CALCULATED';")

# Object view: once the container is visible, initialize and draw synchronously so the first frame cannot be blank.
old="""let lRenderer, lScene, lCamera;
let rocketMesh, exhaustParticles, debrisParticles;
let iipTracePoints = [], iipTraceLine;
let groundPlane, lAnimId, simInterval;

function initLaunchScene() {
  const canvas = document.getElementById('launch-canvas');
  const W = canvas.parentElement.clientWidth, H = canvas.parentElement.clientHeight;"""
new="""let lRenderer, lScene, lCamera;
let rocketMesh, exhaustParticles, debrisParticles;
let iipTracePoints = [], iipTraceLine;
let groundPlane, lAnimId, simInterval;

function resizeLaunchScene(renderNow=false){
  const canvas=document.getElementById('launch-canvas');
  if(!canvas||!lRenderer||!lCamera)return false;
  const W=Math.max(1,canvas.parentElement?.clientWidth||canvas.clientWidth||1),H=Math.max(1,canvas.parentElement?.clientHeight||canvas.clientHeight||1);
  lRenderer.setSize(W,H,false);lCamera.aspect=W/H;lCamera.updateProjectionMatrix();
  if(renderNow&&lScene)lRenderer.render(lScene,lCamera);
  return W>100&&H>100;
}
function markObjectRenderState(state,detail=''){
  const view=document.getElementById('launch-view');if(!view)return;
  view.dataset.renderState=state;view.dataset.renderDetail=detail;
}
function initLaunchScene() {
  const canvas = document.getElementById('launch-canvas');
  if(!canvas)return false;
  const W=Math.max(1,canvas.parentElement.clientWidth), H=Math.max(1,canvas.parentElement.clientHeight);"""
if 'function resizeLaunchScene(' not in source:
    if old not in source: raise SystemExit('launch renderer declaration anchor not found')
    source=source.replace(old,new,1)

old_resize="window.addEventListener('resize',()=>{const W2=canvas.parentElement.clientWidth,H2=canvas.parentElement.clientHeight;lRenderer.setSize(W2,H2);lCamera.aspect=W2/H2;lCamera.updateProjectionMatrix();});\n  animateLaunch();"
new_resize="window.addEventListener('resize',()=>resizeLaunchScene(false));\n  lRenderer.render(lScene,lCamera);\n  markObjectRenderState(W>100&&H>100?'READY':'DEGRADED',`${W}x${H}`);\n  animateLaunch();\n  return true;"
if old_resize in source: source=source.replace(old_resize,new_resize,1)

old_view="if(v==='object'){if(lv){lv.style.display='flex';requestAnimationFrame(()=>lv.classList.add('show'));}requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!lRenderer)initLaunchScene();setTimeout(ensureCorridorOverlay,300);}));return;}"
new_view="""if(v==='object'){
    if(lv){lv.style.display='flex';lv.classList.add('show');markObjectRenderState('INITIALIZING');}
    try{
      if(!lRenderer)initLaunchScene(); else resizeLaunchScene(true);
      markObjectRenderState(lRenderer&&lScene&&lCamera?'READY':'DEGRADED',lRenderer?'renderer-active':'renderer-missing');
      requestAnimationFrame(()=>{resizeLaunchScene(true);ensureCorridorOverlay();});
    }catch(error){markObjectRenderState('ERROR',error?.message||String(error));console.error('[MPL object view]',error);toast('Object view renderer unavailable');}
    return;
  }"""
if old_view in source: source=source.replace(old_view,new_view,1)

# Receipt fallback must reference a real controlled property.
source=source.replace("} catch { MODEL_META.runtimeHash = MODEL_META.baseBlob.slice(0,16); }","} catch { MODEL_META.runtimeHash = MODEL_META.parentSourceSha256.slice(0,16); }")

# Residual visible labels are operational state, not placeholders.
source=source.replace('<th>INS. REQ.</th>','<th>MODEL BUFFER</th>')
source=source.replace('>— W/cm²<','>NOT CALCULATED<')

assert source.count('function hideSatPopup()') == 1
assert source.count('function resizeLaunchScene(') == 1
assert source.count('function markObjectRenderState(') == 1
assert 'MODEL_META.baseBlob' not in source
assert 'v0.' not in source

if source != original:
    path.write_text(source,encoding='utf-8')
    print('Applied pre-release browser acceptance repairs.')
else:
    print('Pre-release browser acceptance repairs already applied.')
