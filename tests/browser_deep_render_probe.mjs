import { chromium } from 'playwright';

const url=process.env.CANDIDATE_URL||'http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1600,height:1000}});
const page=await context.newPage();
const consoleErrors=[];const requestFailures=[];
page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text());});
page.on('requestfailed',r=>requestFailures.push({url:r.url(),error:r.failure()?.errorText||'unknown'}));

const check=(name,ok,detail={})=>{if(!ok)throw new Error(`CHECK_FAILED:${name}:${JSON.stringify(detail)}`);};
await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
await page.waitForFunction(()=>typeof S!=='undefined'&&S.sheetsOk===true&&document.getElementById('app')?.classList.contains('live'),null,{timeout:25000});

const boot=await page.evaluate(()=>({
  sheetsOk:S.sheetsOk,dataMode:MODEL_META.dataMode,enrichmentMode:MODEL_META.enrichmentMode||S.enrichmentMode,
  altitude:S.cameraAltitudeKm,cameraRadius:camera.position.length(),canvas:(()=>{const r=document.getElementById('globe-canvas').getBoundingClientRect();return{w:r.width,h:r.height};})()
}));
check('controlled boot complete',boot.sheetsOk&&boot.dataMode==='CONTROLLED_EMBEDDED_SNAPSHOT'&&boot.enrichmentMode==='CONTROLLED_EMBEDDED_ONLY',boot);
check('globe visible after controlled boot',boot.canvas.w>100&&boot.canvas.h>200,boot.canvas);

// Exercise the actual wheel listener, then the mathematical hard-surface floor.
const wheelBefore=await page.evaluate(()=>S.cameraAltitudeKm);
await page.locator('#globe-canvas').dispatchEvent('wheel',{deltaY:-120});
await page.waitForTimeout(150);
const wheelAfter=await page.evaluate(()=>S.cameraAltitudeKm);
check('wheel zoom reduces altitude',wheelAfter<wheelBefore,{wheelBefore,wheelAfter});
const floor=await page.evaluate(()=>{
  for(let i=0;i<80;i++)zoomCameraBy(2);
  return{alt:S.cameraAltitudeKm,radius:camera.position.length(),near:camera.near,surface:isSurfaceProximity(),atmo:atmoMesh?.visible,
    markersVisible:siteMarkers.some(m=>m.visible)||hvaMarkers.some(m=>m.visible),label:document.getElementById('zoom-ind')?.textContent||''};
});
check('1 km hard-surface floor',Math.abs(floor.alt-1)<1e-9&&floor.radius>1&&floor.near>0&&floor.surface===true,floor);
check('close-surface protrusions suppressed',floor.atmo===false&&floor.markersVisible===false,floor);
check('floor labelled for operator',/ALT 1\.0 km.*FLOOR/.test(floor.label),floor);
await page.evaluate(()=>resetGlobe());

// Prepare a real mission state using the same step renderer that the public UI uses.
await page.evaluate(()=>{
  S.site=SITES[0];S.vehicle=VEHICLES[0];S.transit=TRANSITS[0];S.failModeIds=[];
  renderSites();goStep(2);setView('object');
});
await page.waitForFunction(()=>document.getElementById('launch-view')?.dataset.renderState==='READY',null,{timeout:6000});
const objectView=await page.evaluate(()=>({
  view:S.view,renderer:typeof lRenderer,drawCalls:lRenderer?.info?.render?.calls??0,triangles:lRenderer?.info?.render?.triangles??0,
  renderState:document.getElementById('launch-view')?.dataset.renderState,renderDetail:document.getElementById('launch-view')?.dataset.renderDetail,
  canvas:(()=>{const r=document.getElementById('launch-canvas').getBoundingClientRect();return{w:r.width,h:r.height};})(),display:getComputedStyle(document.getElementById('launch-view')).display
}));
check('object view actively renders',objectView.view==='object'&&objectView.renderer==='object'&&objectView.drawCalls>0&&objectView.canvas.w>100&&objectView.canvas.h>100&&objectView.display!=='none'&&objectView.renderState==='READY',objectView);

// Run the actual simulation fast enough to produce valid orbital state, then force the failure/result path.
await page.evaluate(()=>{startFlightSim();setSimSpeed(8);});
await page.waitForFunction(()=>S.simRunning===true&&simData.alt>5,null,{timeout:10000});
const flight=await page.evaluate(()=>({t:simData.t,alt:simData.alt,vel:simData.vel,running:S.simRunning}));
check('simulation produces nontrivial trajectory',flight.running&&flight.alt>5&&flight.t>0,flight);
await page.evaluate(()=>triggerFailureEvent());
await page.waitForFunction(()=>S.simRunning===false&&Number.isFinite(S.lastRun?.result?.MPL_TOTAL),null,{timeout:8000});

// Orbit view must draw and populate orbital data; a visible empty shell is a soft-break failure.
await page.evaluate(()=>setView('orbit'));
await page.waitForTimeout(350);
const orbit=await page.evaluate(()=>({
  view:S.view,display:getComputedStyle(document.getElementById('orbit-view')).display,nodata:getComputedStyle(document.getElementById('orbit-nodata')).display,
  apo:document.getElementById('ov-apo')?.textContent,per:document.getElementById('ov-per')?.textContent,inc:document.getElementById('ov-inc')?.textContent,
  canvas:(()=>{const c=document.getElementById('orbit-canvas'),r=c.getBoundingClientRect();return{cssW:r.width,cssH:r.height,width:c.width,height:c.height};})()
}));
check('orbit view has computed data',orbit.view==='orbit'&&orbit.display!=='none'&&orbit.nodata==='none'&&!/NOT CALCULATED/.test(`${orbit.apo} ${orbit.per} ${orbit.inc}`),orbit);
check('orbit canvas is internally sized and visible',orbit.canvas.cssW>100&&orbit.canvas.cssH>100&&orbit.canvas.width>100&&orbit.canvas.height>100,orbit.canvas);
await page.evaluate(()=>setView('globe'));

const prohibited=/api\.allorigins\.win|celestrak\.org|eoimages\.gsfc\.nasa\.gov|ssd-api\.jpl\.nasa\.gov|api\.worldbank\.org/i;
const automaticFailures=requestFailures.filter(x=>prohibited.test(x.url));
check('controlled boot has no prohibited automatic enrichment failures',automaticFailures.length===0,{automaticFailures});
const bootErrors=consoleErrors.filter(x=>/\[MPL boot\]|ReferenceError|SyntaxError|TypeError/i.test(x));
check('no core boot/runtime console errors',bootErrors.length===0,{bootErrors});

console.log(JSON.stringify({status:'PASS',boot,wheel:{before:wheelBefore,after:wheelAfter},floor,objectView,flight,orbit,automaticFailures,bootErrors},null,2));
await browser.close();
