import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir=process.env.PROBE_OUT||'artifacts/browser-mpl';
fs.mkdirSync(outDir,{recursive:true});
const candidate=process.env.CANDIDATE_URL||'http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
const context=await browser.newContext({viewport:{width:1600,height:1000},deviceScaleFactor:1});
const page=await context.newPage();
const pageErrors=[],consoleErrors=[],gibsRequests=[];
let failGibs=false;
page.on('pageerror',e=>pageErrors.push(String(e?.stack||e)));
page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
const png1x1=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQmcAAAAASUVORK5CYII=','base64');
await page.route('https://gibs.earthdata.nasa.gov/**',async route=>{
  gibsRequests.push(route.request().url());
  if(failGibs) return route.fulfill({status:503,contentType:'text/plain',body:'test outage'});
  return route.fulfill({status:200,contentType:'image/png',body:png1x1});
});
await page.route('https://script.google.com/**',route=>route.fulfill({status:200,contentType:'application/json',body:'{"ok":true,"acknowledged":true}'}));
await page.route('https://celestrak.org/**',route=>route.fulfill({status:200,contentType:'text/plain',body:''}));

await page.goto(candidate,{waitUntil:'domcontentloaded',timeout:45000});
await page.waitForFunction(()=>document.getElementById('app')?.classList.contains('live'),null,{timeout:30000});
await page.waitForTimeout(900);

const ready=await page.evaluate(async()=>{
  setView('globe');
  S.autoRot=false;
  setCameraAltitudeKm(1);
  clearTimeout(nearSurfaceRefreshTimer);
  await requestNearSurfaceImagery(true);
  return {
    state:nearSurfaceImageryState.status,
    altitude:S.cameraAltitudeKm,
    radialKm:(camera.position.length()-1)*EARTH_RADIUS_KM,
    near:camera.near,
    patch:!!nearSurfacePatch,
    patchVisible:nearSurfacePatch?.visible,
    patchParent:nearSurfacePatch?.parent===globe,
    source:nearSurfaceTexture?.userData?.source,
    sourceResolutionM:nearSurfaceTexture?.userData?.resolutionM,
    requestPixels:nearSurfaceImageryState.pixels,
    spanDeg:nearSurfaceImageryState.spanDeg,
    imageryLayerKm:SURFACE_LAYERS_KM.imagery,
    maxOperationalLayerKm:Math.max(SURFACE_LAYERS_KM.data,SURFACE_LAYERS_KM.graticule,SURFACE_LAYERS_KM.asset,SURFACE_LAYERS_KM.corridor,SURFACE_LAYERS_KM.site,SURFACE_LAYERS_KM.riskHeat,SURFACE_LAYERS_KM.iip,SURFACE_LAYERS_KM.reentry,SURFACE_LAYERS_KM.debris),
    drawCalls:renderer.info.render.calls,
    globeVisible:globe.visible,
    badge:document.getElementById('globe-hd-badge')?.textContent||''
  };
});
if(ready.state!=='READY'||ready.altitude!==1||ready.radialKm<0.9999) throw new Error(`1 km near-surface state failed: ${JSON.stringify(ready)}`);
if(!ready.patch||!ready.patchVisible||!ready.patchParent) throw new Error(`near-surface curved patch missing: ${JSON.stringify(ready)}`);
if(ready.source!=='NASA_GIBS_BLUEMARBLE_NEXTGENERATION'||ready.sourceResolutionM!==500||ready.requestPixels!==2048) throw new Error(`imagery provenance/fidelity mismatch: ${JSON.stringify(ready)}`);
if(!(ready.imageryLayerKm<ready.maxOperationalLayerKm&&ready.maxOperationalLayerKm<1)) throw new Error(`layer ordering reaches camera floor: ${JSON.stringify(ready)}`);
if(!(ready.near>0&&ready.near<(1-ready.imageryLayerKm)/6371)) throw new Error(`near clipping plane unsuitable at 1 km: ${JSON.stringify(ready)}`);
if(!/NASA GIBS.*500 m.*LOCAL DETAIL/.test(ready.badge)) throw new Error(`source badge not explicit: ${ready.badge}`);

const req=new URL(gibsRequests.at(-1));
if(req.searchParams.get('LAYERS')!=='BlueMarble_NextGeneration'||req.searchParams.get('WIDTH')!=='2048'||req.searchParams.get('HEIGHT')!=='2048'||req.searchParams.get('CRS')!=='EPSG:4326') throw new Error(`unexpected GIBS request contract: ${req}`);
const bbox=(req.searchParams.get('BBOX')||'').split(',').map(Number);
if(bbox.length!==4||bbox.some(v=>!Number.isFinite(v))) throw new Error(`invalid GIBS bbox: ${req.searchParams.get('BBOX')}`);

await page.screenshot({path:path.join(outDir,'near-surface-1km.png'),fullPage:false});
const exit=await page.evaluate(()=>{setCameraAltitudeKm(400);return {state:nearSurfaceImageryState.status,visible:nearSurfacePatch?.visible,badge:document.getElementById('globe-hd-badge')?.classList.contains('show')};});
if(exit.state!=='STANDBY'||exit.visible!==false) throw new Error(`near-surface patch did not exit cleanly: ${JSON.stringify(exit)}`);

failGibs=true;
const consoleBeforeOutage=consoleErrors.length;
const fallback=await page.evaluate(async()=>{
  setCameraAltitudeKm(1);clearTimeout(nearSurfaceRefreshTimer);nearSurfaceImageryState.status='ERROR';await requestNearSurfaceImagery(true);await new Promise(r=>setTimeout(r,120));
  return {state:nearSurfaceImageryState.status,error:nearSurfaceImageryState.error,drawCalls:renderer.info.render.calls,globeVisible:globe.visible,badge:document.getElementById('globe-hd-badge')?.textContent||''};
});
if(fallback.state!=='ERROR'||!fallback.globeVisible||fallback.drawCalls<1||!/CONTROLLED GLOBAL/.test(fallback.badge)) throw new Error(`GIBS outage did not preserve controlled fallback: ${JSON.stringify(fallback)}`);
const outageConsoleErrors=consoleErrors.slice(consoleBeforeOutage);
const unexpectedConsoleErrors=consoleErrors.slice(0,consoleBeforeOutage).concat(outageConsoleErrors.filter(e=>!/Failed to load resource:.*503.*Service Unavailable/i.test(e)));
if(pageErrors.length||unexpectedConsoleErrors.length) throw new Error(`browser errors: ${JSON.stringify({pageErrors,unexpectedConsoleErrors,consoleErrors})}`);

const summary={ready,request:req.toString(),exit,fallback,pageErrors,consoleErrors,expectedOutageConsoleErrors:outageConsoleErrors,unexpectedConsoleErrors};
fs.writeFileSync(path.join(outDir,'near-surface-summary.json'),JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
await context.close();
await browser.close();
