from pathlib import Path

PATH = Path('index.html')
source = PATH.read_text(encoding='utf-8')
original = source

# 1. Repair the DOM boundary: #panel was never closed before the collapse button.
old = """        <button class=\"btn-sec\" onclick=\"openSweep()\">⇄ Parameter Sweep</button>\n        <button class=\"btn-sec\" onclick=\"goStep(2)\">← Back</button>\n      </div>\n    <!-- Panel collapse toggle -->"""
new = """        <button class=\"btn-sec\" onclick=\"openSweep()\">⇄ Parameter Sweep</button>\n        <button class=\"btn-sec\" onclick=\"goStep(2)\">← Back</button>\n      </div>\n    </div><!-- /#panel -->\n    <!-- Panel collapse toggle -->"""
if old in source:
    source = source.replace(old, new, 1)
elif '<!-- /#panel -->' not in source:
    raise SystemExit('panel boundary anchor not found')

# 2. Make flex sizing explicit so an iframe or responsive shell cannot collapse the visual viewport.
old = """#globe-canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }\n.globe-wrap { position:relative; min-width:0; min-height:0; contain:layout paint; }"""
new = """#globe-canvas { position:absolute; inset:0; width:100%; height:100%; display:block; }\n.main { flex:1 1 auto; min-width:0; min-height:0; }\n.panel-wrap { height:100%; min-height:0; }\n.panel { height:100%; min-height:0; }\n.globe-wrap { position:relative; flex:1 1 auto; min-width:0; min-height:0; height:100%; contain:layout paint; }"""
if old in source:
    source = source.replace(old, new, 1)
elif '.globe-wrap { position:relative; flex:1 1 auto;' not in source:
    raise SystemExit('globe sizing anchor not found')

# Prefer dynamic viewport units where available without breaking older browsers.
old = """#app {\n  display: flex; flex-direction: column; height: 100vh; min-height: 100%;\n  opacity: 0; transition: opacity 0.7s ease;\n}"""
new = """#app {\n  display: flex; flex-direction: column; height: 100vh; height: 100dvh; min-height: 100%;\n  opacity: 0; transition: opacity 0.7s ease;\n}"""
if old in source:
    source = source.replace(old, new, 1)

# 3. Correct the TopoJSON distribution filename and retain the procedural map if the optional library fails.
source = source.replace(
    'https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson.min.js',
    'https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js',
    1,
)
old = """async function loadTopoJSONMap() {\n  const badge = document.getElementById('globe-hd-badge');\n  if(badge){ badge.textContent='LOADING VECTOR MAP…'; badge.classList.add('show'); }"""
new = """async function loadTopoJSONMap() {\n  const badge = document.getElementById('globe-hd-badge');\n  if(typeof topojson === 'undefined') {\n    console.warn('[MPL map] TopoJSON client unavailable; retaining deterministic procedural map.');\n    if(badge){ badge.textContent='PROCEDURAL MAP · VECTOR ENRICHMENT UNAVAILABLE'; badge.classList.add('show'); setTimeout(()=>badge.classList.remove('show'),2200); }\n    setTimeout(loadHDGlobeTexture, 200);\n    return;\n  }\n  if(badge){ badge.textContent='LOADING VECTOR MAP…'; badge.classList.add('show'); }"""
if old in source:
    source = source.replace(old, new, 1)
elif "TopoJSON client unavailable" not in source:
    raise SystemExit('TopoJSON function anchor not found')

# 4. Eliminate the hoisting recursion in the GDP overlay dispatcher.
old = 'function buildGDPOverlay() {\n  if(gdpOverlayMesh){ scene.remove(gdpOverlayMesh); gdpOverlayMesh=null; }'
new = 'function buildGDPHaloOverlay() {\n  if(gdpOverlayMesh){ scene.remove(gdpOverlayMesh); gdpOverlayMesh=null; }'
if old in source:
    source = source.replace(old, new, 1)
elif 'function buildGDPHaloOverlay()' not in source:
    raise SystemExit('base GDP overlay anchor not found')
old = """// Rebuild GDP overlay with choropleth support (extends existing buildGDPOverlay)\nconst _baseGDPOverlay = buildGDPOverlay;\nfunction buildGDPOverlay() {\n  if(gdpChoroMode === 'choropleth') return buildGDPChoropleth();\n  return _baseGDPOverlay(); // existing halo mode\n}"""
new = """// Rebuild GDP overlay with choropleth support without function-hoisting recursion.\nfunction buildGDPOverlay() {\n  if(gdpChoroMode === 'choropleth') return buildGDPChoropleth();\n  return buildGDPHaloOverlay();\n}"""
if old in source:
    source = source.replace(old, new, 1)
elif 'return buildGDPHaloOverlay();' not in source:
    raise SystemExit('GDP dispatcher anchor not found')

# 5. Replace broken cross-origin cloud images with a deterministic same-document procedural layer.
start = source.find('function buildCloudLayer() {')
end_marker = "\n}\n\n/* ════════════════════════════════════════════════════════\n   BC-011: EXTENDED KEYBOARD SHORTCUTS"
end = source.find(end_marker, start)
if start < 0 or end < 0:
    if 'PROCEDURAL CLOUD LAYER' not in source:
        raise SystemExit('cloud layer anchors not found')
else:
    replacement = r'''function buildCloudLayer() {
  if(cloudMesh){ scene.remove(cloudMesh); cloudMesh.geometry?.dispose?.(); cloudMesh.material?.map?.dispose?.(); cloudMesh.material?.dispose?.(); cloudMesh=null; }
  if(!scene || typeof THREE==='undefined') return;

  // PROCEDURAL CLOUD LAYER — no remote texture or CORS dependency.
  // A seeded generator keeps screenshots and mission receipts deterministic.
  const W=2048,H=1024,cv=document.createElement('canvas'); cv.width=W; cv.height=H;
  const ctx=cv.getContext('2d'); ctx.clearRect(0,0,W,H);
  let seed=0x524f4d45;
  const rand=()=>{ seed=(1664525*seed+1013904223)>>>0; return seed/4294967296; };
  ctx.globalCompositeOperation='lighter';
  for(let band=0;band<9;band++){
    const centreY=H*(0.12+band*0.095)+(rand()-.5)*55;
    const clusters=24+Math.floor(rand()*18);
    for(let c=0;c<clusters;c++){
      const cx=rand()*W, cy=centreY+(rand()-.5)*150;
      const rx=35+rand()*130, ry=8+rand()*32;
      const g=ctx.createRadialGradient(cx,cy,0,cx,cy,rx);
      const alpha=0.035+rand()*0.055;
      g.addColorStop(0,`rgba(230,242,255,${alpha})`);
      g.addColorStop(0.45,`rgba(210,232,250,${alpha*.62})`);
      g.addColorStop(1,'rgba(190,220,245,0)');
      ctx.save(); ctx.translate(cx,cy); ctx.scale(1,ry/rx); ctx.beginPath(); ctx.arc(0,0,rx,0,Math.PI*2); ctx.restore();
      ctx.fillStyle=g; ctx.fill();
    }
  }
  ctx.globalCompositeOperation='source-over';
  const tex=new THREE.CanvasTexture(cv);
  tex.minFilter=THREE.LinearFilter; tex.magFilter=THREE.LinearFilter;
  const mat=new THREE.MeshPhongMaterial({map:tex,transparent:true,opacity:0.48,depthWrite:false,side:THREE.FrontSide,blending:THREE.NormalBlending});
  cloudMesh=new THREE.Mesh(new THREE.SphereGeometry(1.018,64,64),mat);
  cloudMesh.visible=S.settings.clouds===true;
  cloudMesh.userData.cloudDrift=true;
  scene.add(cloudMesh);
}'''
    source = source[:start] + replacement + source[end+2:]

# 6. Add a simple visible runtime health receipt for front-facing QA.
needle = """  renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:false});\n  renderer.setSize(W,H,false); renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2.25));"""
replacement = """  renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:false});\n  renderer.setSize(W,H,false); renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2.25));\n  canvas.dataset.webgl='ready';\n  canvas.addEventListener('webglcontextlost',()=>{canvas.dataset.webgl='lost';dataBadge('WEBGL CONTEXT LOST','var(--red)');},{passive:true});\n  canvas.addEventListener('webglcontextrestored',()=>{canvas.dataset.webgl='restored';dataBadge('WEBGL RESTORED','var(--green)');requestAnimationFrame(resizeGlobe);},{passive:true});"""
if needle in source:
    source = source.replace(needle, replacement, 1)

if source == original:
    print('No changes required; repair already applied.')
else:
    PATH.write_text(source, encoding='utf-8')
    print(f'Patched {PATH}: {len(original)} -> {len(source)} chars')
