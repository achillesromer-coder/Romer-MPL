import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir=process.env.PROBE_OUT||'artifacts/browser-mpl';
fs.mkdirSync(outDir,{recursive:true});
const candidate=process.env.CANDIDATE_URL||'http://127.0.0.1:4173/index.html';
const targets=[
  {name:'candidate-desktop',url:candidate,viewport:{width:1600,height:1000},mobile:false,enforce:true},
  {name:'candidate-mobile',url:candidate,viewport:{width:430,height:932},mobile:true,enforce:true},
];
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
const summary=[]; let hardFailure=false;

for(const target of targets){
  const context=await browser.newContext({viewport:target.viewport,deviceScaleFactor:1});
  const page=await context.newPage();
  const pageErrors=[],consoleErrors=[],requestFailures=[],writeReceipts=[];
  page.on('pageerror',e=>pageErrors.push(String(e?.stack||e)));
  page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
  page.on('requestfailed',r=>requestFailures.push({url:r.url(),error:r.failure()?.errorText||'unknown'}));
  await page.route('https://script.google.com/**',async route=>{
    const req=route.request();
    if(req.method()==='POST'){
      try{writeReceipts.push(JSON.parse(req.postData()||'{}'));}catch{writeReceipts.push({unparsed:req.postData()||''});}
    }
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,acknowledged:true,testTransport:true})});
  });
  await page.route('https://celestrak.org/**',route=>route.fulfill({status:200,contentType:'text/plain',body:''}));

  let navError=null;
  try{
    await page.goto(target.url,{waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForFunction(()=>document.getElementById('app')?.classList.contains('live'),null,{timeout:30000});
    await page.waitForTimeout(1400);
  }catch(err){navError=String(err?.stack||err);}

  const checks={};
  const run=async(name,fn)=>{
    try{checks[name]={ok:true,value:await fn()};}
    catch(err){checks[name]={ok:false,error:String(err?.stack||err)};hardFailure=true;}
  };

  await run('boot-contract',()=>page.evaluate(()=>{
    const canvas=document.getElementById('globe-canvas'); const rect=canvas?.getBoundingClientRect();
    const gl=canvas?.getContext?.('webgl2')||canvas?.getContext?.('webgl');
    if(!canvas||!rect||rect.width<200||rect.height<250) throw new Error(`invalid globe canvas ${rect?.width}x${rect?.height}`);
    if(canvas.closest('.panel-wrap')) throw new Error('globe canvas nested in panel');
    if(document.querySelector('.telebar')?.parentElement?.id!=='app') throw new Error('telemetry bar outside app shell');
    if(typeof THREE!=='object'||typeof renderer!=='object'||typeof scene!=='object'||typeof camera!=='object') throw new Error('Three/WebGL globals unavailable');
    if(!gl||gl.isContextLost()) throw new Error('WebGL context unavailable/lost');
    if(!(renderer.info?.render?.calls>0)) throw new Error('renderer has not produced draw calls');
    if(document.title!=='Römer MPL Platform — Pre-release') throw new Error(`unexpected title ${document.title}`);
    if(document.querySelector('.tb-stage')?.textContent?.trim()!=='PRE-RELEASE') throw new Error('pre-release stage missing');
    const counts={sites:WORKBOOK_SNAPSHOT.sites.length,vehicles:WORKBOOK_SNAPSHOT.vehicles.length,population:WORKBOOK_SNAPSHOT.population.length,assets:WORKBOOK_SNAPSHOT.assets.length,failureModes:WORKBOOK_SNAPSHOT.failureModes.length,operators:WORKBOOK_SNAPSHOT.operators.length,bridge:WORKBOOK_SNAPSHOT.bridge.length,gdp:Object.keys(WORKBOOK_SNAPSHOT.gdp).length};
    const expected={sites:15,vehicles:6,population:148,assets:25,failureModes:12,operators:4,bridge:2,gdp:154};
    for(const [k,v] of Object.entries(expected))if(counts[k]!==v)throw new Error(`${k} ${counts[k]} != ${v}`);
    const overflow=document.documentElement.scrollWidth-document.documentElement.clientWidth;
    if(overflow>2) throw new Error(`horizontal overflow ${overflow}px`);
    return {canvas:{w:rect.width,h:rect.height},drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,counts,dataMode:MODEL_META.dataMode,snapshot:MODEL_META.workbookSnapshotSha256,webgl:gl.getParameter(gl.VERSION)};
  }));

  await run('step-guard-and-site-navigation',()=>page.evaluate(()=>{
    newMission(); goStep(2); if(S.step!==1) throw new Error('step 2 opened without site');
    selectSiteById('LS005'); if(S.site?.id!=='LS005')throw new Error('LS005 selection failed');
    confirmSite(); if(S.step!==2)throw new Error('site confirmation did not open step 2');
    selTransit('LAUNCH_ORBIT'); selVehicle('V001'); goStep(3); if(S.step!==3)throw new Error('step 3 did not open');
    if(document.getElementById('panel-step').textContent!=='Mission Setup — Step 3 of 3')throw new Error('step label inconsistent');
    return {step:S.step,site:S.site.id,vehicle:S.vehicle.id,transit:S.transit.id};
  }));

  await run('side-panel-collapse-expand',async()=>{
    const initial=await page.evaluate(()=>({collapsed:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
    const before=await page.locator('#globe-canvas').boundingBox();
    if(initial.collapsed){
      // Mobile boots collapsed by design: verify expand first, then restore the intended collapsed state.
      await page.locator('#panel-toggle').click(); await page.waitForTimeout(650);
      const expandedBox=await page.locator('#globe-canvas').boundingBox();
      const expanded=await page.evaluate(()=>({state:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
      if(expanded.state||expanded.expanded!=='true')throw new Error('panel did not expand semantically from collapsed boot');
      await page.locator('#panel-toggle').click(); await page.waitForTimeout(650);
      const collapsedBox=await page.locator('#globe-canvas').boundingBox();
      const collapsed=await page.evaluate(()=>({state:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
      if(!collapsed.state||collapsed.expanded!=='false')throw new Error('panel did not re-collapse semantically');
      if(target.mobile&&collapsedBox.width<target.viewport.width-4)throw new Error(`mobile collapsed globe is not full width: ${collapsedBox.width}`);
      return {initial:'collapsed',before:before.width,expanded:expandedBox.width,collapsed:collapsedBox.width};
    }
    await page.locator('#panel-toggle').click(); await page.waitForTimeout(650);
    const collapsedBox=await page.locator('#globe-canvas').boundingBox();
    const collapsed=await page.evaluate(()=>({state:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
    if(!collapsed.state||collapsed.expanded!=='false')throw new Error('panel did not collapse semantically');
    if(!target.mobile&&!(collapsedBox.width>before.width+150))throw new Error(`desktop globe did not expand ${before.width}->${collapsedBox.width}`);
    await page.locator('#panel-toggle').click(); await page.waitForTimeout(650);
    const expandedBox=await page.locator('#globe-canvas').boundingBox();
    const expanded=await page.evaluate(()=>({state:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
    if(expanded.state||expanded.expanded!=='true')throw new Error('panel did not expand semantically');
    return {initial:'expanded',before:before.width,collapsed:collapsedBox.width,expanded:expandedBox.width};
  });

  await run('hard-surface-zoom',()=>page.evaluate(()=>{
    setView('globe'); setCameraAltitudeKm(25); for(let i=0;i<80;i++)doZoom(1.2);
    const min=S.cameraAltitudeKm; const radialAlt=(camera.position.length()-1)*EARTH_RADIUS_KM;
    if(Math.abs(min-1)>1e-9||radialAlt<0.9999)throw new Error(`camera penetrated hard surface: state=${min}, radial=${radialAlt}`);
    if(cloudMesh?.visible)throw new Error('cloud shell visible below near-surface threshold');
    if(atmoMeshes.some(m=>m.visible))throw new Error('atmosphere shell visible below near-surface threshold');
    const maxSurface=Math.max(SURFACE_LAYERS_KM.data,SURFACE_LAYERS_KM.graticule,SURFACE_LAYERS_KM.asset,SURFACE_LAYERS_KM.corridor,SURFACE_LAYERS_KM.site,SURFACE_LAYERS_KM.riskHeat,SURFACE_LAYERS_KM.iip,SURFACE_LAYERS_KM.reentry,SURFACE_LAYERS_KM.debris);
    if(maxSurface>=CAMERA_LIMITS.minAltitudeKm)throw new Error(`surface overlay ${maxSurface}km reaches camera floor`);
    resetGlobe(); if(S.cameraAltitudeKm!==10000)throw new Error('reset altitude mismatch');
    return {floorKm:min,radialKm:radialAlt,maxSurfaceLayerKm:maxSurface,resetKm:S.cameraAltitudeKm};
  }));

  await run('view-switching-object-orbit',async()=>{
    await page.evaluate(()=>{newMission();setView('object');});
    let v=await page.evaluate(()=>S.view); if(v!=='globe')throw new Error('object view opened without site');
    await page.evaluate(()=>{selectSiteById('LS005');confirmSite();selTransit('LAUNCH_ORBIT');selVehicle('V001');setView('object');});
    await page.waitForTimeout(1000);
    const obj=await page.evaluate(()=>{
      const rect=document.getElementById('launch-canvas')?.getBoundingClientRect();
      return {view:S.view,renderer:!!lRenderer,scene:!!lScene,width:rect?.width||0,height:rect?.height||0,display:getComputedStyle(document.getElementById('launch-view')).display,drawCalls:lRenderer?.info?.render?.calls||0};
    });
    if(obj.view!=='object'||!obj.renderer||!obj.scene||obj.width<200||obj.height<200||obj.display==='none'||obj.drawCalls<1)throw new Error(`Object view did not initialise: ${JSON.stringify(obj)}`);
    await page.evaluate(()=>{setView('orbit');renderOrbitView();}); await page.waitForTimeout(250);
    const noData=await page.evaluate(()=>getComputedStyle(document.getElementById('orbit-nodata')).display);
    if(noData==='none')throw new Error('Orbit no-data state not rendered before trajectory exists');
    await page.evaluate(()=>{simData={...simData,t:500,alt:250,vel:7600,pitch:0,phase:'DOWNRANGE',iipLat:-30,iipLon:140};renderOrbitView();}); await page.waitForTimeout(250);
    const withData=await page.evaluate(()=>({view:S.view,noData:getComputedStyle(document.getElementById('orbit-nodata')).display,pressed:document.getElementById('vbtn-orbit').getAttribute('aria-pressed')}));
    if(withData.noData!=='none'||withData.pressed!=='true')throw new Error('Orbit populated state/view semantics failed');
    await page.evaluate(()=>setView('globe'));
    return {object:obj,orbit:withData};
  });

  await run('model-phase-and-override-contract',()=>page.evaluate(()=>{
    const site=WORKBOOK_SNAPSHOT.sites.find(s=>s.id==='LS005');const vehicle={...WORKBOOK_SNAPSHOT.vehicles.find(v=>v.id==='V001'),ac:1724};
    S.advSecMult=ASA.SECONDARY_MULT;S.advIA=0;
    const up=calculateMPL({vehicle,site,phase:'UPRANGE',zone:'URBAN',failModes:[],isUprange:true});
    const coast=calculateMPL({vehicle,site,phase:'COAST',zone:'URBAN',failModes:['FM-012'],isUprange:false});
    const ret=calculateMPL({vehicle,site,phase:'DESCENT',zone:'URBAN',failModes:['FM-012'],isUprange:false});
    if(up.CAS_primary!==1||up.CAS_secondary!==2||up.CAS_total!==3)throw new Error('uprange casualty parity failed');
    if(coast.phaseClass!=='DOWNRANGE'||coast.CAS_secondary!==0||coast.MPL_PD!==0||coast.MPL_LOU!==0||coast.MPL_ENV!==0||!coast.ignoredFailureModes.includes('FM-012'))throw new Error('downrange phase/inclusion contract failed');
    if(ret.phaseClass!=='RETURN'||!ret.selectedFailureModes.includes('FM-012')||ret.MPL_PD<=0||ret.MPL_LOU<=0||ret.MPL_ENV<=0)throw new Error('return phase contract failed');
    if(ret.methodEvidence.impactIsopleth10e7!==false||ret.methodEvidence.hvaScreeningMethod!=='ROMER_SCREENING_HEURISTIC')throw new Error('regulatory geometry boundary failed');
    const constant=ASA.SECONDARY_MULT;const v2={...vehicle,ac:3000};S.advSecMult=2;const ov=calculateMPL({vehicle:v2,site,phase:'UPRANGE',zone:'URBAN',failModes:[],isUprange:true});S.advSecMult=constant;
    if(ov.CAS_primary!==2||ov.CAS_secondary!==4||ASA.SECONDARY_MULT!==constant)throw new Error('scenario override leaked into controlled constants');
    return {up:{p:up.CAS_primary,s:up.CAS_secondary,t:up.CAS_total},coast:{ignored:coast.ignoredFailureModes},ret:{selected:ret.selectedFailureModes},buffer:ret.MODEL_BUFFER};
  }));

  if(!target.mobile){
    await run('mission-run-results',async()=>{
      await page.evaluate(()=>{newMission();selectSiteById('LS005');confirmSite();selTransit('LAUNCH_ORBIT');selVehicle('V001');S.failMode='set';S.failModeIds=['FM-001'];document.getElementById('fail-t').value='1';S.simSpeed=8;});
      await page.evaluate(()=>runMission());
      await page.waitForFunction(()=>S.lastRun&&S.simRunning===false,null,{timeout:12000});
      await page.waitForTimeout(1100);
      const r=await page.evaluate(()=>({runId:S.lastRun?.runId,total:S.lastRun?.result?.MPL_TOTAL,phase:S.lastRun?.result?.phase,shown:document.getElementById('mpl-results').classList.contains('show'),status:document.getElementById('t-status').textContent,history:RUN_HISTORY.length}));
      if(!r.runId||!(r.total>=0)||!r.shown||r.status!=='MISHAP'||r.history<1)throw new Error('mission run did not reach rendered mishap result');
      return r;
    });

    await run('sweep-evidence-batch-modals',()=>page.evaluate(()=>{
      openSweep();document.getElementById('sw-axis').value='zone';document.getElementById('sw-fm').value='ALL';runSweep();
      if(sweepResults.length!==5||document.getElementById('sw-export-btn').disabled)throw new Error('zone sweep failed');closeSweep();
      openEvidenceReview();runEvidenceReview();const evidence=document.getElementById('evidence-output').textContent;if(!/10⁻⁷|isopleth/i.test(evidence))throw new Error('evidence review omitted hazard geometry dependency');closeEvidenceReview();
      openBatch();loadBatchPreset('achilles_targets');if(BATCH_QUEUE.length!==WORKBOOK_SNAPSHOT.bridge.length)throw new Error('ACHILLES preset count mismatch');runBatch();
      if(batchResults.length!==2||batchResults.some(r=>!r.siteId||!r.vehicleId))throw new Error('batch result identity mismatch');closeBatch();
      openRuns();if(document.getElementById('runs-modal').style.display!=='flex')throw new Error('runs modal did not open');closeRuns();
      openVehEditor();if(document.getElementById('veh-editor-modal').style.display!=='flex')throw new Error('vehicle editor did not open');closeVehEditor();
      openSettings();if(!document.getElementById('settings-modal').classList.contains('open'))throw new Error('settings did not open');closeSettings();
      return {sweep:sweepResults.length,batch:batchResults.length,evidence:true,runs:RUN_HISTORY.length};
    }));

    await run('acknowledged-write-transport',async()=>{
      await page.evaluate(()=>logMissionRun()); await page.waitForTimeout(500);
      const tabs=writeReceipts.map(x=>x.tab||x.action||'').filter(Boolean);
      if(!writeReceipts.some(x=>x.tab==='Mission_Log'))throw new Error('Mission_Log write not attempted through acknowledged test transport');
      return {writes:writeReceipts.length,tabs};
    });
  }else{
    await run('mobile-panel-default',async()=>{
      await page.waitForTimeout(500);
      const state=await page.evaluate(()=>({collapsed:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded'),canvas:document.getElementById('globe-canvas').getBoundingClientRect().width,viewport:innerWidth}));
      // Prior tests may have expanded panel; verify it can still be collapsed to the intended mobile state.
      if(!state.collapsed)await page.locator('#panel-toggle').click();
      await page.waitForTimeout(500);
      const after=await page.evaluate(()=>({collapsed:S.panelCollapsed,expanded:document.getElementById('panel-toggle').getAttribute('aria-expanded'),canvas:document.getElementById('globe-canvas').getBoundingClientRect().width,viewport:innerWidth}));
      if(!after.collapsed||after.expanded!=='false'||after.canvas<after.viewport-4)throw new Error('mobile panel/full-width globe state failed');
      return after;
    });
  }

  const record={target,navError,checks,pageErrors,consoleErrors,requestFailures,writeReceipts};
  fs.writeFileSync(path.join(outDir,`${target.name}.json`),JSON.stringify(record,null,2));
  await page.screenshot({path:path.join(outDir,`${target.name}.png`),fullPage:true}).catch(()=>{});
  summary.push(record);
  if(navError||pageErrors.length||consoleErrors.length||requestFailures.length)hardFailure=true;
  await context.close();
}
fs.writeFileSync(path.join(outDir,'summary.json'),JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary.map(r=>({target:r.target.name,navError:r.navError,failed:Object.entries(r.checks).filter(([,v])=>!v.ok).map(([k,v])=>({check:k,error:v.error})),pageErrors:r.pageErrors,consoleErrors:r.consoleErrors})),null,2));
await browser.close();if(hardFailure)process.exit(2);
