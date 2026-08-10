from pathlib import Path

P = Path('index.html')
s = P.read_text(encoding='utf-8')
MARK = 'ADAPTIVE NEAR-SURFACE IMAGERY'
if MARK in s:
    raise SystemExit('near-surface fidelity already applied')

old = """const SURFACE_LAYERS_KM = Object.freeze({
  data:0.04, graticule:0.06, asset:0.08, corridor:0.10, site:0.12,
  riskHeat:0.14, iip:0.15, reentry:0.16, debris:0.18, cloud:12,
  atmosphereLow:80, atmosphereMid:160, atmosphereHigh:300,
});"""
new = """const SURFACE_LAYERS_KM = Object.freeze({
  imagery:0.012, data:0.04, graticule:0.06, asset:0.08, corridor:0.10, site:0.12,
  riskHeat:0.14, iip:0.15, reentry:0.16, debris:0.18, cloud:12,
  atmosphereLow:80, atmosphereMid:160, atmosphereHigh:300,
});
const NEAR_SURFACE_IMAGERY = Object.freeze({
  enabled:true, enterAltitudeKm:300, exitAltitudeKm:360,
  source:'NASA_GIBS_BLUEMARBLE_NEXTGENERATION', sourceResolutionM:500,
  service:'WMS_1_3_0_EPSG4326', endpoint:'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi',
  layer:'BlueMarble_NextGeneration', minRequestPixels:1024, maxRequestPixels:2048,
  refreshFraction:0.22, patchOverscan:1.28, requestTimeoutMs:12000,
});"""
assert old in s
s = s.replace(old, new, 1)

old = """function updateNearSurfaceLayers(){
  const nearSurface=S.cameraAltitudeKm < 25;
  if(cloudMesh) cloudMesh.visible=!nearSurface && S.settings.clouds===true;
  atmoMeshes.forEach(m=>{m.visible=!nearSurface && S.showAtmo && S.settings.atmo!==false;});
  const scale=surfaceMarkerScale();
  [...siteMarkers,...hvaMarkers].forEach(m=>{if(m.userData?.surfaceMarker)m.scale.setScalar(scale);});
}"""
new = old[:-2] + "  updateNearSurfaceImageryVisibility();\n}"
assert old in s
s = s.replace(old, new, 1)

anchor = '\n\n/* ─── RASTER ZONES ─── */'
assert anchor in s
impl = r'''

/* ─── ADAPTIVE NEAR-SURFACE IMAGERY ───
   Natural Earth remains the deterministic global fallback. Below 300 km a curved local
   patch requests NASA GIBS Blue Marble Next Generation context (500 m source product)
   around the camera nadir. This layer is visual context only and is excluded from MPL
   calculations, model evidence, and regulatory claims. */
let nearSurfacePatch=null, nearSurfaceTexture=null;
let nearSurfaceImageryState={status:'STANDBY',source:NEAR_SURFACE_IMAGERY.source,center:null,spanDeg:null,pixels:null,lastKey:null,requestSeq:0,error:null};
let nearSurfaceRefreshTimer=null, nearSurfaceFrameCounter=0;
function globeLocalNadirLatLon(){
  if(!camera||!globe) return S.site&&Number.isFinite(Number(S.site.lat))&&Number.isFinite(Number(S.site.lon))?{lat:Number(S.site.lat),lon:Number(S.site.lon)}:{lat:0,lon:0};
  const local=camera.position.clone().normalize(); const inv=globe.quaternion.clone();
  if(typeof inv.invert==='function') inv.invert(); else inv.inverse(); local.applyQuaternion(inv).normalize();
  return {lat:Math.asin(Math.max(-1,Math.min(1,local.y)))*180/Math.PI,lon:Math.atan2(-local.z,local.x)*180/Math.PI};
}
function nearSurfaceHorizonRadiusDeg(altitudeKm){const h=Math.max(CAMERA_LIMITS.minAltitudeKm,finiteNumber(altitudeKm,CAMERA_LIMITS.defaultAltitudeKm));return Math.acos(EARTH_RADIUS_KM/(EARTH_RADIUS_KM+h))*180/Math.PI;}
function nearSurfaceRequestSpec(){
  const center=globeLocalNadirLatLon(),horizon=Math.max(0.35,nearSurfaceHorizonRadiusDeg(S.cameraAltitudeKm));
  const latHalf=Math.min(35,horizon*NEAR_SURFACE_IMAGERY.patchOverscan),cosLat=Math.max(0.22,Math.cos(center.lat*Math.PI/180));
  const lonHalf=Math.min(65,latHalf/cosLat),pixels=S.cameraAltitudeKm<=50?NEAR_SURFACE_IMAGERY.maxRequestPixels:S.cameraAltitudeKm<=150?1536:NEAR_SURFACE_IMAGERY.minRequestPixels;
  return {center,latHalf,lonHalf,pixels};
}
function normalizeLon180(lon){return ((lon+180)%360+360)%360-180;}
function nearSurfaceAngularDelta(a,b){const d=Math.abs(normalizeLon180(a)-normalizeLon180(b));return Math.min(d,360-d);}
function shouldRefreshNearSurfaceImagery(spec){
  const prev=nearSurfaceImageryState.center;if(!prev||!nearSurfaceImageryState.spanDeg||nearSurfaceImageryState.status==='ERROR')return true;
  const threshold=Math.max(0.05,nearSurfaceImageryState.spanDeg*NEAR_SURFACE_IMAGERY.refreshFraction);
  return Math.abs(spec.center.lat-prev.lat)>threshold||nearSurfaceAngularDelta(spec.center.lon,prev.lon)>threshold||spec.pixels!==nearSurfaceImageryState.pixels;
}
function updateNearSurfaceSourceBadge(message,visible=true){const badge=document.getElementById('globe-hd-badge');if(!badge)return;if(message)badge.textContent=message;badge.classList.toggle('show',Boolean(visible));}
function disposeNearSurfacePatch(){
  if(nearSurfacePatch){nearSurfacePatch.parent?.remove?.(nearSurfacePatch);nearSurfacePatch.geometry?.dispose?.();nearSurfacePatch.material?.dispose?.();nearSurfacePatch=null;}
  if(nearSurfaceTexture){nearSurfaceTexture.dispose?.();nearSurfaceTexture.userData?.bitmap?.close?.();nearSurfaceTexture=null;}
}
function buildCurvedImageryPatch(spec,texture){
  if(!globe||typeof THREE==='undefined')return null;
  const latMin=Math.max(-89.8,spec.center.lat-spec.latHalf),latMax=Math.min(89.8,spec.center.lat+spec.latHalf),lonStart=spec.center.lon-spec.lonHalf,lonSpan=spec.lonHalf*2;
  const seg=Math.max(40,Math.min(96,Math.round(48+spec.lonHalf))),positions=[],uvs=[],indices=[];
  for(let iy=0;iy<=seg;iy++){const fy=iy/seg,lat=latMax-(latMax-latMin)*fy;for(let ix=0;ix<=seg;ix++){const fx=ix/seg,lon=normalizeLon180(lonStart+lonSpan*fx),v=ll2v3(lat,lon,radiusAtAltitudeKm(SURFACE_LAYERS_KM.imagery));positions.push(v.x,v.y,v.z);uvs.push(fx,1-fy);}}
  for(let iy=0;iy<seg;iy++)for(let ix=0;ix<seg;ix++){const a=iy*(seg+1)+ix,b=a+1,c=a+seg+1,d=c+1;indices.push(a,c,b,b,c,d);}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute(uvs,2));geo.setIndex(indices);geo.computeVertexNormals();
  const mat=new THREE.MeshBasicMaterial({map:texture,depthWrite:true,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1});
  const mesh=new THREE.Mesh(geo,mat);mesh.name='NASA GIBS near-surface imagery';mesh.renderOrder=1;mesh.userData={nearSurfaceImagery:true,visualOnly:true};return mesh;
}
function nasaGibsWmsUrl(spec){
  const latMin=Math.max(-89.8,spec.center.lat-spec.latHalf),latMax=Math.min(89.8,spec.center.lat+spec.latHalf),lonMin=spec.center.lon-spec.lonHalf,lonMax=spec.center.lon+spec.lonHalf;
  const params=new URLSearchParams({SERVICE:'WMS',REQUEST:'GetMap',VERSION:'1.3.0',LAYERS:NEAR_SURFACE_IMAGERY.layer,STYLES:'',FORMAT:'image/jpeg',TRANSPARENT:'FALSE',CRS:'EPSG:4326',BBOX:`${latMin.toFixed(6)},${lonMin.toFixed(6)},${latMax.toFixed(6)},${lonMax.toFixed(6)}`,WIDTH:String(spec.pixels),HEIGHT:String(spec.pixels)});
  return `${NEAR_SURFACE_IMAGERY.endpoint}?${params.toString()}`;
}
async function requestNearSurfaceImagery(force=false){
  if(!NEAR_SURFACE_IMAGERY.enabled||!globe||S.cameraAltitudeKm>NEAR_SURFACE_IMAGERY.exitAltitudeKm)return false;
  const spec=nearSurfaceRequestSpec();if(!force&&!shouldRefreshNearSurfaceImagery(spec))return nearSurfaceImageryState.status==='READY';
  const seq=++nearSurfaceImageryState.requestSeq,key=`${spec.center.lat.toFixed(3)}:${spec.center.lon.toFixed(3)}:${spec.pixels}`;
  nearSurfaceImageryState={...nearSurfaceImageryState,status:'LOADING',center:spec.center,spanDeg:spec.latHalf*2,pixels:spec.pixels,lastKey:key,error:null};
  updateNearSurfaceSourceBadge(`NASA GIBS · BMNG 500 m · ${formatCameraAltitude(S.cameraAltitudeKm).replace('ALT ','')}`,true);
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),NEAR_SURFACE_IMAGERY.requestTimeoutMs);
  try{
    const response=await fetch(nasaGibsWmsUrl(spec),{mode:'cors',cache:'force-cache',signal:controller.signal,referrerPolicy:'no-referrer'});if(!response.ok)throw new Error(`GIBS HTTP ${response.status}`);
    const blob=await response.blob();if(!/^image\//i.test(blob.type))throw new Error(`GIBS returned ${blob.type||'non-image content'}`);const bitmap=await createImageBitmap(blob);if(seq!==nearSurfaceImageryState.requestSeq){bitmap.close?.();return false;}
    const tex=new THREE.Texture(bitmap);tex.needsUpdate=true;tex.minFilter=THREE.LinearMipMapLinearFilter;tex.magFilter=THREE.LinearFilter;tex.anisotropy=renderer?renderer.capabilities.getMaxAnisotropy():16;tex.userData={bitmap,source:NEAR_SURFACE_IMAGERY.source,resolutionM:NEAR_SURFACE_IMAGERY.sourceResolutionM};if('encoding' in tex)tex.encoding=THREE.sRGBEncoding;
    const mesh=buildCurvedImageryPatch(spec,tex);if(!mesh)throw new Error('Near-surface patch geometry unavailable');disposeNearSurfacePatch();nearSurfaceTexture=tex;nearSurfacePatch=mesh;globe.add(mesh);nearSurfaceImageryState={...nearSurfaceImageryState,status:'READY',error:null};updateNearSurfaceSourceBadge('NASA GIBS · BMNG 500 m · LOCAL DETAIL',true);return true;
  }catch(err){if(seq!==nearSurfaceImageryState.requestSeq)return false;nearSurfaceImageryState={...nearSurfaceImageryState,status:'ERROR',error:String(err?.message||err)};updateNearSurfaceSourceBadge('LOCAL DETAIL UNAVAILABLE · CONTROLLED GLOBAL',true);return false;}finally{clearTimeout(timeout);}
}
function scheduleNearSurfaceImageryRefresh(force=false){clearTimeout(nearSurfaceRefreshTimer);nearSurfaceRefreshTimer=setTimeout(()=>requestNearSurfaceImagery(force),force?0:180);}
function updateNearSurfaceImageryVisibility(){
  if(!NEAR_SURFACE_IMAGERY.enabled)return;
  if(S.cameraAltitudeKm<=NEAR_SURFACE_IMAGERY.enterAltitudeKm){if(nearSurfacePatch)nearSurfacePatch.visible=true;scheduleNearSurfaceImageryRefresh(false);}
  else if(S.cameraAltitudeKm>NEAR_SURFACE_IMAGERY.exitAltitudeKm){if(nearSurfacePatch)nearSurfacePatch.visible=false;if(nearSurfaceImageryState.status!=='STANDBY')nearSurfaceImageryState={...nearSurfaceImageryState,status:'STANDBY'};const badge=document.getElementById('globe-hd-badge');if(badge&&/NASA GIBS|LOCAL DETAIL/.test(badge.textContent||''))badge.classList.remove('show');}
}
'''
s = s.replace(anchor, impl + anchor, 1)

s = s.replace("canvas.addEventListener('mouseup',()=>S.drag=false);", "canvas.addEventListener('mouseup',()=>{S.drag=false;scheduleNearSurfaceImageryRefresh(false);});", 1)
s = s.replace("canvas.addEventListener('mouseleave',()=>{S.drag=false;hideSatPopup();});", "canvas.addEventListener('mouseleave',()=>{S.drag=false;hideSatPopup();scheduleNearSurfaceImageryRefresh(false);});", 1)
s = s.replace("function setupMouse(canvas){\n  let px,py;", "function setupMouse(canvas){\n  let px,py,pinchDistance=null;", 1)
old_touch = """  canvas.addEventListener('touchstart',e=>{S.drag=true;S.autoRot=false;px=e.touches[0].clientX;py=e.touches[0].clientY;},{passive:true});
  canvas.addEventListener('touchmove',e=>{
    if(!S.drag)return;
    const dx=(e.touches[0].clientX-px)*0.005, dy=(e.touches[0].clientY-py)*0.005;
    globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));
    userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));
    px=e.touches[0].clientX;py=e.touches[0].clientY;
  },{passive:true});
  canvas.addEventListener('touchend',()=>S.drag=false);"""
new_touch = """  canvas.addEventListener('touchstart',e=>{S.drag=true;S.autoRot=false;px=e.touches[0].clientX;py=e.touches[0].clientY;pinchDistance=e.touches.length>=2?Math.hypot(e.touches[1].clientX-e.touches[0].clientX,e.touches[1].clientY-e.touches[0].clientY):null;},{passive:true});
  canvas.addEventListener('touchmove',e=>{
    if(!S.drag)return;
    if(e.touches.length>=2){const d=Math.hypot(e.touches[1].clientX-e.touches[0].clientX,e.touches[1].clientY-e.touches[0].clientY);if(pinchDistance&&d>0)setCameraAltitudeKm(S.cameraAltitudeKm*Math.max(0.82,Math.min(1.22,pinchDistance/d)));pinchDistance=d;return;}
    const dx=(e.touches[0].clientX-px)*0.005, dy=(e.touches[0].clientY-py)*0.005;globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));px=e.touches[0].clientX;py=e.touches[0].clientY;
  },{passive:true});
  canvas.addEventListener('touchend',e=>{if(e.touches.length<2)pinchDistance=null;if(e.touches.length===0){S.drag=false;scheduleNearSurfaceImageryRefresh(false);}});"""
assert old_touch in s
s = s.replace(old_touch, new_touch, 1)

needle = """  // Satellites — update at 2Hz via real ECI propagation
  satUpdateCounter++;"""
assert needle in s
s = s.replace(needle, """  if(S.cameraAltitudeKm<=NEAR_SURFACE_IMAGERY.enterAltitudeKm && !S.drag && (++nearSurfaceFrameCounter%120===0)) scheduleNearSurfaceImageryRefresh(false);

  // Satellites — update at 2Hz via real ECI propagation
  satUpdateCounter++;""", 1)

s = s.replace("  for(let i=1;i<=steps;i++){await wait(18);const e=1-Math.pow(1-i/steps,3);setCameraAltitudeKm(start+(target-start)*e);}\n}", "  for(let i=1;i<=steps;i++){await wait(18);const e=1-Math.pow(1-i/steps,3);setCameraAltitudeKm(start+(target-start)*e);}\n  scheduleNearSurfaceImageryRefresh(true);\n}", 1)
s = s.replace("display:none;letter-spacing:.06em;", "display:none;letter-spacing:.06em;z-index:18;pointer-events:none;", 1)
s = s.replace("Interactive Earth risk-screening globe. Camera altitude is constrained to at least one kilometre above mean Earth radius; this camera limit is a Römer rendering control, not an Australian Space Agency regulatory altitude.", "Interactive Earth risk-screening globe. Camera altitude is constrained to at least one kilometre above mean Earth radius; this camera limit is a Römer rendering control, not an Australian Space Agency regulatory altitude. Below 300 kilometres, NASA GIBS Blue Marble Next Generation imagery is requested for local visual context with the controlled Natural Earth globe retained as fallback.", 1)

P.write_text(s, encoding='utf-8')
print(f'applied near-surface fidelity: {len(s.encode())} bytes')