import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir=process.env.PROBE_OUT||'artifacts/browser-globe';
fs.mkdirSync(outDir,{recursive:true});
const candidate=process.env.CANDIDATE_URL||'http://127.0.0.1:4173/index.html';
const targets=[
  {name:'candidate-desktop',url:candidate,viewport:{width:1600,height:1000},enforce:true,fullFlow:true},
  {name:'candidate-mobile',url:candidate,viewport:{width:430,height:932},enforce:true,fullFlow:false},
  {name:'github-pages-live',url:'https://achillesromer-coder.github.io/Romer-MPL/',viewport:{width:1600,height:1000},enforce:false,fullFlow:false},
  {name:'squarespace-live',url:'https://romer.industries/mpl-engine',viewport:{width:1600,height:1000},enforce:false,fullFlow:false},
];

const browser=await chromium.launch({headless:true,args:['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']});
const summary=[];let hardFailure=false;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));

async function snapshot(frame){
  return frame.evaluate(()=>{
    const rect=id=>{const r=document.getElementById(id)?.getBoundingClientRect?.();return r?{x:r.x,y:r.y,width:r.width,height:r.height}:null;};
    const canvas=document.getElementById('globe-canvas');
    let glState={exists:false},rendererState={},globals={};
    try{
      globals={THREE:typeof THREE,renderer:typeof renderer,scene:typeof scene,camera:typeof camera,globe:typeof globe};
      if(typeof renderer!=='undefined'&&renderer)rendererState={calls:renderer.info?.render?.calls??null,triangles:renderer.info?.render?.triangles??null,width:renderer.domElement?.width??null,height:renderer.domElement?.height??null};
      const gl=canvas?.getContext?.('webgl2')||canvas?.getContext?.('webgl');
      if(gl)glState={exists:true,lost:gl.isContextLost(),version:gl.getParameter(gl.VERSION)};
    }catch(error){rendererState.probeError=String(error?.stack||error);}
    return {
      href:location.href,title:document.title,readyState:document.readyState,
      stageText:document.querySelector('.tb-stage')?.textContent||null,
      appClass:document.getElementById('app')?.className||'',
      canvas:rect('globe-canvas'),panel:rect('panel'),launch:rect('launch-view'),orbit:rect('orbit-view'),
      globeInsidePanel:Boolean(canvas?.closest('.panel-wrap')),
      telemetryParent:document.querySelector('.telebar')?.parentElement?.id||null,
      globals,rendererState,glState,
      state:typeof S!=='undefined'?{view:S.view,step:S.step,panelCollapsed:S.panelCollapsed,cameraAltitudeKm:S.cameraAltitudeKm,sheetsOk:S.sheetsOk,site:S.site?.id||null,vehicle:S.vehicle?.id||null,transit:S.transit?.id||null,simRunning:S.simRunning,lastRun:Number.isFinite(S.lastRun?.result?.MPL_TOTAL)?S.lastRun.result.MPL_TOTAL:null}:null,
      dataMode:typeof MODEL_META!=='undefined'?MODEL_META.dataMode:null,
      runtimeHash:typeof MODEL_META!=='undefined'?MODEL_META.runtimeHash:null,
      cameraRadius:typeof camera!=='undefined'&&camera?camera.position.length():null,
      cameraNear:typeof camera!=='undefined'&&camera?camera.near:null,
      visibleText:(document.body?.innerText||'').slice(0,12000),
    };
  });
}

async function exerciseCandidate(frame,target){
  const receipt={checks:[]};
  const check=(name,ok,detail={})=>{receipt.checks.push({name,ok:Boolean(ok),...detail});if(!ok)throw new Error(`CHECK_FAILED:${name}:${JSON.stringify(detail)}`);};
  await frame.waitForFunction(()=>typeof S!=='undefined'&&document.getElementById('app')?.classList.contains('live'),null,{timeout:25000});
  let state=await snapshot(frame);
  check('pre-release identity',state.stageText==='PRE-RELEASE'&&!/v\d/i.test(state.title),{stage:state.stageText,title:state.title});
  check('controlled embedded data',state.dataMode==='CONTROLLED_EMBEDDED_SNAPSHOT'&&state.state?.sheetsOk===true,{dataMode:state.dataMode,sheetsOk:state.state?.sheetsOk});
  check('globe canvas visible',state.canvas?.width>100&&state.canvas?.height>200,{canvas:state.canvas});
  check('WebGL healthy',state.glState.exists===true&&state.glState.lost===false&&state.rendererState.calls>0,{gl:state.glState,renderer:state.rendererState});
  check('DOM topology',state.globeInsidePanel===false&&state.telemetryParent==='app',{globeInsidePanel:state.globeInsidePanel,telemetryParent:state.telemetryParent});

  // Side navigation / panel geometry. Mobile boots collapsed; desktop boots expanded.
  const initialPanel=await frame.evaluate(()=>({collapsed:S.panelCollapsed,canvas:document.getElementById('globe-canvas').getBoundingClientRect().width}));
  await frame.locator('#panel-toggle').click({timeout:5000});await frame.waitForTimeout(650);
  const toggledPanel=await frame.evaluate(()=>({collapsed:S.panelCollapsed,canvas:document.getElementById('globe-canvas').getBoundingClientRect().width,aria:document.getElementById('panel-toggle').getAttribute('aria-expanded')}));
  check('panel toggle state changes',initialPanel.collapsed!==toggledPanel.collapsed,{initialPanel,toggledPanel});
  check('panel toggle accessibility',toggledPanel.aria===String(!toggledPanel.collapsed),{aria:toggledPanel.aria,collapsed:toggledPanel.collapsed});
  await frame.locator('#panel-toggle').click({timeout:5000});await frame.waitForTimeout(650);

  // User-facing zoom button changes altitude; repeated zoom clamps at the 1 km Römer visualization floor.
  const alt0=await frame.evaluate(()=>S.cameraAltitudeKm);
  await frame.locator('button[title^="Zoom in"]').click({timeout:5000});await frame.waitForTimeout(250);
  const alt1=await frame.evaluate(()=>S.cameraAltitudeKm);
  check('zoom-in button reduces altitude',alt1<alt0,{alt0,alt1});
  const floor=await frame.evaluate(()=>{for(let i=0;i<80;i++)zoomCameraBy(2);return{alt:S.cameraAltitudeKm,radius:camera.position.length(),near:camera.near,label:document.getElementById('zoom-ind')?.textContent};});
  check('camera floor clamps at 1 km',Math.abs(floor.alt-1)<1e-9,{floor});
  check('camera never enters globe',floor.radius>1&&floor.near>0,{floor});
  check('camera floor is visible to operator',/1\.0 km.*FLOOR/.test(floor.label||''),{label:floor.label});
  await frame.locator('button[title^="Reset view"]').click({timeout:5000});await frame.waitForTimeout(250);
  const resetAlt=await frame.evaluate(()=>S.cameraAltitudeKm);
  check('reset restores controlled initial altitude',Math.abs(resetAlt-11500)<1e-6,{resetAlt});

  // Object view must not silently render blank when no site has been chosen.
  await frame.locator('#vbtn-o').click({timeout:5000});await frame.waitForTimeout(250);
  const rejected=await frame.evaluate(()=>({view:S.view,toast:document.getElementById('toast')?.textContent||''}));
  check('object view rejects missing site',rejected.view==='globe'&&/Select a launch site/i.test(rejected.toast),rejected);

  if(!target.fullFlow){
    // On mobile the mission panel is an overlay and the full globe remains the primary surface.
    const mobile=await snapshot(frame);
    check('responsive globe retains usable width',mobile.canvas.width>=target.viewport.width-2,{canvas:mobile.canvas,viewport:target.viewport});
    return receipt;
  }

  // Step 1: actual site-row click and confirm button.
  await frame.locator('#site-list .site-row').first().click({timeout:6000});await frame.waitForTimeout(300);
  let mission=await frame.evaluate(()=>({site:S.site?.id,card:document.getElementById('site-card').classList.contains('show'),alt:S.cameraAltitudeKm}));
  check('site selection binds state and card',Boolean(mission.site)&&mission.card,mission);
  await frame.getByRole('button',{name:/Confirm Site/}).click({timeout:6000});await frame.waitForTimeout(250);
  check('site confirmation advances to step 2',await frame.evaluate(()=>S.step===2&&getComputedStyle(document.getElementById('body-s2')).display!=='none'));

  // Step 2: real transit, vehicle and failure-mode controls.
  await frame.locator('#transit-list .transit-opt').first().click({timeout:6000});
  await frame.locator('#vehicle-grid .vehicle-card').first().click({timeout:6000});
  await frame.locator('#fm-list .fm-item').first().click({timeout:6000});
  mission=await frame.evaluate(()=>({transit:S.transit?.id,vehicle:S.vehicle?.id,failModes:[...S.failModeIds]}));
  check('mission controls bind transit vehicle and failure mode',Boolean(mission.transit&&mission.vehicle&&mission.failModes.length),mission);

  // View navigation beyond initial globe.
  await frame.locator('#vbtn-o').click({timeout:6000});await frame.waitForTimeout(900);
  let viewState=await frame.evaluate(()=>({view:S.view,launchDisplay:getComputedStyle(document.getElementById('launch-view')).display,lRenderer:typeof lRenderer,launchRect:(()=>{const r=document.getElementById('launch-canvas').getBoundingClientRect();return{w:r.width,h:r.height}})()}));
  check('object view renders',viewState.view==='object'&&viewState.launchDisplay!=='none'&&viewState.lRenderer==='object'&&viewState.launchRect.w>100&&viewState.launchRect.h>100,viewState);
  await frame.locator('#vbtn-orbit').click({timeout:6000});await frame.waitForTimeout(650);
  viewState=await frame.evaluate(()=>({view:S.view,display:getComputedStyle(document.getElementById('orbit-view')).display,rect:(()=>{const r=document.getElementById('orbit-view').getBoundingClientRect();return{w:r.width,h:r.height}})()}));
  check('orbit view shell renders without silent blank',viewState.view==='orbit'&&viewState.display!=='none'&&viewState.rect.w>100&&viewState.rect.h>100,viewState);
  await frame.locator('#vbtn-g').click({timeout:6000});await frame.waitForTimeout(300);
  check('globe view restores',await frame.evaluate(()=>S.view==='globe'));

  // Step 3 and sweep execution.
  await frame.getByRole('button',{name:/Advanced Parameters/}).click({timeout:6000});await frame.waitForTimeout(200);
  check('advanced navigation reaches step 3',await frame.evaluate(()=>S.step===3));
  await frame.getByRole('button',{name:/Parameter Sweep/}).click({timeout:6000});await frame.waitForTimeout(200);
  check('sweep modal opens',await frame.evaluate(()=>getComputedStyle(document.getElementById('sweep-modal')).display!=='none'));
  await frame.getByRole('button',{name:'Run Sweep',exact:true}).click({timeout:6000});await frame.waitForTimeout(400);
  const sweep=await frame.evaluate(()=>({rows:typeof sweepResults!=='undefined'?sweepResults.length:0,text:document.getElementById('sweep-results')?.innerText||'',undefinedText:/undefined|NaN/.test(document.getElementById('sweep-results')?.innerText||'')}));
  check('parameter sweep returns finite rendered rows',sweep.rows>0&&!sweep.undefinedText&&/A\$/.test(sweep.text),sweep);
  await frame.evaluate(()=>closeSweep());

  // Vehicle editor, settings, run history and batch navigation surfaces.
  await frame.evaluate(()=>goStep(2));
  await frame.getByRole('button',{name:'+ CUSTOM',exact:true}).click({timeout:6000});await frame.waitForTimeout(150);
  check('vehicle editor opens',await frame.evaluate(()=>getComputedStyle(document.getElementById('veh-editor-modal')).display!=='none'));
  await frame.evaluate(()=>closeVehEditor());
  await frame.locator('button[title="Settings"]').click({timeout:6000});await frame.waitForTimeout(150);
  check('settings modal opens',await frame.evaluate(()=>document.getElementById('settings-modal').classList.contains('open')));
  await frame.evaluate(()=>closeSettings());
  await frame.locator('button[title="Run History"]').click({timeout:6000});await frame.waitForTimeout(150);
  check('runs modal opens',await frame.evaluate(()=>getComputedStyle(document.getElementById('runs-modal')).display!=='none'));
  await frame.evaluate(()=>closeRuns());
  await frame.page().keyboard.press('b');await frame.waitForTimeout(180);
  check('batch keyboard navigation opens modal',await frame.evaluate(()=>getComputedStyle(document.getElementById('batch-modal')).display!=='none'));
  await frame.evaluate(()=>{addBatchItem();runBatch();});await frame.waitForTimeout(400);
  const batch=await frame.evaluate(()=>({queue:BATCH_QUEUE.length,results:batchResults.length,text:document.getElementById('batch-results-panel')?.innerText||''}));
  check('batch calculation renders',batch.queue>0&&batch.results>0&&!/undefined|NaN/.test(batch.text),batch);
  await frame.evaluate(()=>closeBatch());

  // Main run path: actual Run Simulation control -> object view -> simulation -> forced failure -> result surface.
  await frame.evaluate(()=>goStep(2));
  await frame.getByRole('button',{name:/Run Simulation/}).click({timeout:6000});
  await frame.waitForFunction(()=>S.simRunning===true&&S.view==='object',null,{timeout:8000});
  const started=await frame.evaluate(()=>({running:S.simRunning,view:S.view,alt:S.cameraAltitudeKm,lRenderer:typeof lRenderer}));
  check('run path starts simulation in object view',started.running&&started.view==='object'&&started.lRenderer==='object',started);
  check('site focus remains above hard surface',started.alt>=1,{alt:started.alt});
  await frame.evaluate(()=>triggerFailureEvent());await frame.waitForTimeout(1250);
  const result=await frame.evaluate(()=>({running:S.simRunning,mpl:S.lastRun?.result?.MPL_TOTAL,display:getComputedStyle(document.getElementById('mpl-results')).display,text:document.getElementById('mpl-results')?.innerText||''}));
  check('failure path produces finite MPL result',result.running===false&&Number.isFinite(result.mpl)&&result.mpl>=0&&result.display!=='none'&&!/undefined|NaN/.test(result.text),{running:result.running,mpl:result.mpl,display:result.display});

  // Deterministic evidence review; no external AI provider is invoked.
  await frame.evaluate(()=>{openAI();runAIAnalysis();});await frame.waitForTimeout(200);
  const evidence=await frame.evaluate(()=>document.getElementById('ai-output')?.innerText||'');
  check('deterministic evidence review renders',/MODEL EVIDENCE REVIEW/.test(evidence)&&!/Claude|Anthropic/i.test(evidence),{evidence:evidence.slice(0,500)});
  await frame.evaluate(()=>closeAI());

  // New mission returns every key operational field to an explicit state.
  await frame.locator('button[title="New mission"]').click({timeout:6000});await frame.waitForTimeout(250);
  const reset=await frame.evaluate(()=>({site:S.site,vehicle:S.vehicle,transit:S.transit,step:S.step,view:S.view,tele:['t-site','t-vehicle','t-phase','t-iip','t-mpl-exp'].map(id=>document.getElementById(id)?.textContent)}));
  check('new mission clears mission state',!reset.site&&!reset.vehicle&&!reset.transit&&reset.step===1,reset);
  check('new mission uses explicit telemetry states',reset.tele.every(v=>v&&v!=='—'&&!/undefined|NaN/.test(v)),{tele:reset.tele});

  const visible=await frame.evaluate(()=>document.body?.innerText||'');
  check('no visible undefined or NaN',!/\bundefined\b|\bNaN\b/.test(visible));
  return receipt;
}

for(const target of targets){
  const context=await browser.newContext({viewport:target.viewport,deviceScaleFactor:1});
  const page=await context.newPage();
  const consoleEvents=[],pageErrors=[],requestFailures=[],badResponses=[];
  page.on('console',m=>consoleEvents.push({type:m.type(),text:m.text()}));
  page.on('pageerror',e=>pageErrors.push({message:e.message,stack:e.stack||''}));
  page.on('requestfailed',r=>requestFailures.push({url:r.url(),failure:r.failure()?.errorText||'unknown'}));
  page.on('response',r=>{if(r.status()>=400)badResponses.push({url:r.url(),status:r.status()});});
  let navError=null;
  try{await page.goto(target.url,{waitUntil:'domcontentloaded',timeout:45000});await page.waitForTimeout(12000);}catch(error){navError=String(error?.stack||error);}
  const frames=page.frames().map(f=>({name:f.name(),url:f.url()}));
  let appFrame=page.mainFrame();
  if(target.name==='squarespace-live')appFrame=page.frames().find(f=>/achillesromer-coder\.github\.io\/Romer-MPL/.test(f.url()))||appFrame;
  const diagnostic=await snapshot(appFrame).catch(error=>({probeError:String(error?.stack||error),href:appFrame.url()}));
  let exercise=null,exerciseError=null;
  if(target.name.startsWith('candidate-')){
    try{exercise=await exerciseCandidate(appFrame,target);}catch(error){exerciseError=String(error?.stack||error);}
  }
  await page.screenshot({path:path.join(outDir,`${target.name}.png`),fullPage:true}).catch(()=>{});
  const record={target,navError,frames,diagnostic,exercise,exerciseError,pageErrors,requestFailures,badResponses,console:consoleEvents};
  fs.writeFileSync(path.join(outDir,`${target.name}.json`),JSON.stringify(record,null,2));
  summary.push(record);
  if(target.enforce){
    const d=diagnostic||{};
    const functionalErrors=pageErrors.filter(e=>/Maximum call stack|ReferenceError|SyntaxError|TypeError|is not defined/i.test(e.message));
    const failedChecks=exercise?.checks?.filter(c=>!c.ok)||[];
    const failure=Boolean(navError)||Boolean(d.probeError)||Boolean(exerciseError)||failedChecks.length>0||functionalErrors.length>0||!d.canvas||!(d.canvas.width>100&&d.canvas.height>200)||d.globeInsidePanel||d.telemetryParent!=='app'||d.glState?.exists!==true||d.glState?.lost===true;
    hardFailure ||= failure;
  }
  await context.close();
}

fs.writeFileSync(path.join(outDir,'summary.json'),JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
await browser.close();
if(hardFailure)process.exit(2);
