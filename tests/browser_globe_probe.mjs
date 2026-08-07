import { chromium } from 'playwright';
import fs from 'node:fs';
import path from 'node:path';

const outDir = process.env.PROBE_OUT || 'artifacts/browser-globe';
fs.mkdirSync(outDir, { recursive: true });
const candidate = process.env.CANDIDATE_URL || 'http://127.0.0.1:4173/index.html';
const targets = [
  { name: 'candidate-desktop', url: candidate, viewport: { width: 1600, height: 1000 }, enforce: true },
  { name: 'candidate-mobile', url: candidate, viewport: { width: 430, height: 932 }, enforce: true },
  { name: 'github-pages-live', url: 'https://achillesromer-coder.github.io/Romer-MPL/', viewport: { width: 1600, height: 1000 }, enforce: false },
  { name: 'squarespace-live', url: 'https://romer.industries/mpl-engine', viewport: { width: 1600, height: 1000 }, enforce: false },
];

const browser = await chromium.launch({
  headless: true,
  args: ['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'],
});
const summary=[];
let hardFailure=false;

for (const target of targets) {
  const context=await browser.newContext({viewport:target.viewport,deviceScaleFactor:1});
  const page=await context.newPage();
  const consoleEvents=[], pageErrors=[], requestFailures=[], badResponses=[];
  page.on('console',m=>consoleEvents.push({type:m.type(),text:m.text()}));
  page.on('pageerror',e=>pageErrors.push({message:e.message,stack:e.stack||''}));
  page.on('requestfailed',r=>requestFailures.push({url:r.url(),failure:r.failure()?.errorText||'unknown'}));
  page.on('response',r=>{if(r.status()>=400)badResponses.push({url:r.url(),status:r.status()});});

  let navError=null;
  try {
    await page.goto(target.url,{waitUntil:'domcontentloaded',timeout:45000});
    await page.waitForTimeout(12000);
  } catch(err) { navError=String(err?.stack||err); }

  const frames=page.frames().map(f=>({name:f.name(),url:f.url()}));
  let appFrame=page.mainFrame();
  if(target.name==='squarespace-live') appFrame=page.frames().find(f=>/achillesromer-coder\.github\.io\/Romer-MPL/.test(f.url()))||appFrame;

  const diag=await appFrame.evaluate(()=>{
    const canvas=document.getElementById('globe-canvas');
    const wrap=canvas?.parentElement;
    const panelWrap=document.querySelector('.panel-wrap');
    const tele=document.querySelector('.telebar');
    const canvasRect=canvas?.getBoundingClientRect?.();
    const wrapRect=wrap?.getBoundingClientRect?.();
    const panelRect=panelWrap?.getBoundingClientRect?.();
    let globals={},rendererState={},sceneState={},contextState={};
    try {
      globals={THREE:typeof THREE,threeRevision:typeof THREE!=='undefined'?THREE.REVISION:null,renderer:typeof renderer,scene:typeof scene,camera:typeof camera,globe:typeof globe};
      if(typeof renderer!=='undefined'&&renderer) rendererState={width:renderer.domElement?.width||null,height:renderer.domElement?.height||null,calls:renderer.info?.render?.calls??null,triangles:renderer.info?.render?.triangles??null,memoryGeometries:renderer.info?.memory?.geometries??null,memoryTextures:renderer.info?.memory?.textures??null};
      if(typeof scene!=='undefined'&&scene) sceneState={children:scene.children?.length??null};
      const gl=canvas?.getContext?.('webgl2')||canvas?.getContext?.('webgl');
      if(gl){const dbg=gl.getExtension('WEBGL_debug_renderer_info');contextState={exists:true,lost:gl.isContextLost(),version:gl.getParameter(gl.VERSION),vendor:dbg?gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL):gl.getParameter(gl.VENDOR),renderer:dbg?gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};} else contextState={exists:false};
    } catch(err){rendererState.probeError=String(err?.stack||err);}
    const chain=[]; let node=canvas?.parentElement; while(node&&chain.length<8){chain.push({tag:node.tagName,id:node.id||null,classes:[...node.classList]});node=node.parentElement;}
    return {
      href:location.href,title:document.title,readyState:document.readyState,versionText:document.querySelector('.tb-version')?.textContent||null,
      splash:{display:getComputedStyle(document.getElementById('splash')).display,opacity:getComputedStyle(document.getElementById('splash')).opacity},
      app:{className:document.getElementById('app')?.className||'',opacity:getComputedStyle(document.getElementById('app')).opacity},
      canvas:canvas?{present:true,widthAttr:canvas.width,heightAttr:canvas.height,webglState:canvas.dataset.webgl||null,rect:canvasRect?{x:canvasRect.x,y:canvasRect.y,width:canvasRect.width,height:canvasRect.height}:null,css:{width:getComputedStyle(canvas).width,height:getComputedStyle(canvas).height,display:getComputedStyle(canvas).display}}:{present:false},
      wrap:wrapRect?{width:wrapRect.width,height:wrapRect.height}:null,
      panelWrap:panelRect?{width:panelRect.width,height:panelRect.height}:null,
      ancestorChain:chain,
      globeInsidePanel:Boolean(canvas?.closest('.panel-wrap')),
      telemetryParent:tele?.parentElement?.id||tele?.parentElement?.className||null,
      globals,rendererState,sceneState,contextState,
      scriptSrcs:[...document.scripts].map(s=>s.src).filter(Boolean),
    };
  }).catch(err=>({probeError:String(err?.stack||err),href:appFrame.url()}));

  // Front-facing interaction smoke: use native controls without depending on data transport.
  const interactions={};
  if(target.name.startsWith('candidate-')) {
    try {
      const before=await appFrame.evaluate(()=>({zoom:typeof S!=='undefined'?S.zoom:null,panelCollapsed:typeof S!=='undefined'?S.panelCollapsed:null}));
      await appFrame.locator('.gc-btn').first().click({timeout:4000}).catch(()=>{});
      await appFrame.waitForTimeout(350);
      const after=await appFrame.evaluate(()=>({zoom:typeof S!=='undefined'?S.zoom:null,panelCollapsed:typeof S!=='undefined'?S.panelCollapsed:null}));
      interactions.before=before; interactions.after=after;
    } catch(err){interactions.error=String(err?.stack||err);}
  }

  await page.screenshot({path:path.join(outDir,`${target.name}.png`),fullPage:true}).catch(()=>{});
  const record={target,navError,frames,diagnostic:diag,interactions,pageErrors,requestFailures,badResponses,console:consoleEvents};
  fs.writeFileSync(path.join(outDir,`${target.name}.json`),JSON.stringify(record,null,2));
  summary.push(record);

  if(target.enforce){
    const d=diag||{};
    const functionalErrors=pageErrors.filter(e=>/topojson is not defined|Maximum call stack|buildGDPOverlay/i.test(e.message));
    const failure=Boolean(navError)||Boolean(d.probeError)||!d.canvas?.present||!(d.canvas?.rect?.width>100&&d.canvas?.rect?.height>200)||d.globeInsidePanel||d.telemetryParent!=='app'||d.globals?.THREE!=='object'||d.globals?.renderer!=='object'||d.globals?.scene!=='object'||d.contextState?.exists!==true||d.contextState?.lost===true||!(d.rendererState?.calls>0)||!(d.sceneState?.children>0)||functionalErrors.length>0;
    hardFailure ||= failure;
  }
  await context.close();
}

fs.writeFileSync(path.join(outDir,'summary.json'),JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
await browser.close();
if(hardFailure)process.exit(2);
