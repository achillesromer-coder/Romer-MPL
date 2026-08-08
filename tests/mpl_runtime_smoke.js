const fs=require('fs');
const vm=require('vm');
const crypto=require('crypto');

const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const code=scripts.at(-1);
if(!code) throw new Error('Inline application script not found');

const noop=()=>{};
function element(){
  return new Proxy({
    style:{},dataset:{},children:[],textContent:'',innerHTML:'',value:'',checked:false,disabled:false,
    classList:{add:noop,remove:noop,toggle:noop,contains:()=>false},appendChild:noop,remove:noop,setAttribute:noop,getAttribute:()=>null,
    addEventListener:noop,removeEventListener:noop,querySelector:()=>null,querySelectorAll:()=>[],
    getBoundingClientRect:()=>({width:1200,height:800,left:0,top:0,right:1200,bottom:800}),getContext:()=>null,parentElement:null,focus:noop,click:noop
  },{get:(t,k)=>k in t?t[k]:noop,set:(t,k,v)=>(t[k]=v,true)});
}
const elements=new Map();
const document={
  documentElement:{outerHTML:html},body:element(),head:element(),
  getElementById:id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id)},
  querySelector:()=>null,querySelectorAll:()=>[],createElement:()=>element(),createElementNS:()=>element(),addEventListener:noop,removeEventListener:noop
};
const location={hash:'',href:'https://example.test',search:'',pathname:'/'};
const windowObject={addEventListener:noop,removeEventListener:noop,innerWidth:1600,innerHeight:1000,devicePixelRatio:1,location,history:{replaceState:noop},open:noop,matchMedia:()=>({matches:false,addEventListener:noop,removeEventListener:noop})};
const context={
  console,document,window:windowObject,location,navigator:{userAgent:'node-smoke',clipboard:{writeText:noop}},
  fetch:async()=>({ok:false,status:503,text:async()=>'',json:async()=>({})}),localStorage:{getItem:()=>null,setItem:noop,removeItem:noop},sessionStorage:{getItem:()=>null,setItem:noop},
  setTimeout:()=>0,clearTimeout:noop,setInterval:()=>0,clearInterval:noop,requestAnimationFrame:()=>0,cancelAnimationFrame:noop,
  AbortSignal:{timeout:()=>({})},confirm:()=>false,alert:noop,URL,URLSearchParams,TextEncoder,TextDecoder,crypto:crypto.webcrypto,Blob:global.Blob,
  performance:{now:()=>0},ResizeObserver:class{observe(){}disconnect(){}},Image:class{},FileReader:class{},atob:global.atob,btoa:global.btoa
};
context.globalThis=context;
vm.createContext(context);
vm.runInContext(code,context,{timeout:15000});
const ev=expr=>vm.runInContext(expr,context,{timeout:10000});

const receipt=ev(`(() => {
  const counts={sites:WORKBOOK_SNAPSHOT.sites.length,vehicles:WORKBOOK_SNAPSHOT.vehicles.length,population:WORKBOOK_SNAPSHOT.population.length,assets:WORKBOOK_SNAPSHOT.assets.length,failureModes:WORKBOOK_SNAPSHOT.failureModes.length,operators:WORKBOOK_SNAPSHOT.operators.length,bridge:WORKBOOK_SNAPSHOT.bridge.length,gdp:Object.keys(WORKBOOK_SNAPSHOT.gdp).length};
  const expected={sites:15,vehicles:6,population:148,assets:25,failureModes:12,operators:4,bridge:2,gdp:154};
  for(const k of Object.keys(expected)) if(counts[k]!==expected[k]) throw new Error('snapshot count '+k+'='+counts[k]+' expected '+expected[k]);
  if(WORKBOOK_SNAPSHOT.meta.sha256!=='ab8749b3505b25d651d3641bc612eef64acc2ff891822e05d447c511b876bb7c') throw new Error('snapshot receipt mismatch');
  if(CAMERA_LIMITS.minAltitudeKm!==1) throw new Error('camera floor is not 1 km');
  if(Math.abs((radiusAtAltitudeKm(1)-1)*EARTH_RADIUS_KM-1)>1e-9) throw new Error('physical radius conversion failed');
  if(!(SURFACE_LAYERS_KM.debris<1&&SURFACE_LAYERS_KM.riskHeat<1&&SURFACE_LAYERS_KM.iip<1)) throw new Error('surface overlay exceeds camera floor');
  const site=WORKBOOK_SNAPSHOT.sites.find(s=>s.id==='LS005');
  const vehicle={...WORKBOOK_SNAPSHOT.vehicles.find(v=>v.id==='V001'),ac:1724};
  S.advSecMult=ASA.SECONDARY_MULT;S.advIA=0;
  const up=calculateMPL({vehicle,site,phase:'UPRANGE',zone:'URBAN',failModes:[],isUprange:true});
  if(up.CAS_primary!==1||up.CAS_secondary!==2||up.CAS_total!==3) throw new Error('uprange casualty rule mismatch');
  const coast=calculateMPL({vehicle,site,phase:'COAST',zone:'URBAN',failModes:['FM-012'],isUprange:false});
  if(coast.phaseClass!=='DOWNRANGE'||coast.CAS_secondary!==0||coast.MPL_PD!==0||coast.MPL_LOU!==0||coast.MPL_ENV!==0) throw new Error('downrange inclusion rule mismatch');
  if(!coast.ignoredFailureModes.includes('FM-012')||coast.selectedFailureModes.length) throw new Error('phase-incompatible failure mode not ignored');
  const ret=calculateMPL({vehicle,site,phase:'DESCENT',zone:'URBAN',failModes:['FM-012'],isUprange:false});
  if(ret.phaseClass!=='RETURN'||ret.CAS_secondary!==0||ret.MPL_PD<=0||ret.MPL_LOU<=0||ret.MPL_ENV<=0) throw new Error('return phase rule mismatch');
  if(!ret.selectedFailureModes.includes('FM-012')) throw new Error('return failure mode missing');
  if(ret.methodEvidence.impactIsopleth10e7!==false||ret.methodEvidence.hvaRegulatoryInclusion!==false||ret.methodEvidence.hvaScreeningMethod!=='ROMER_SCREENING_HEURISTIC') throw new Error('HVA evidence boundary mismatch');
  if(Math.abs(ret.MODEL_BUFFER/ret.MPL_TOTAL-ASA.MODEL_BUFFER_FACTOR)>0.01) throw new Error('planning buffer mismatch');
  const constant=ASA.SECONDARY_MULT;
  const v2={...vehicle,ac:3000};S.advSecMult=constant;
  const base=calculateMPL({vehicle:v2,site,phase:'UPRANGE',zone:'URBAN',failModes:[],isUprange:true});
  S.advSecMult=2.0;
  const overridden=calculateMPL({vehicle:v2,site,phase:'UPRANGE',zone:'URBAN',failModes:[],isUprange:true});
  if(base.CAS_primary!==2||base.CAS_secondary!==3||overridden.CAS_secondary!==4||ASA.SECONDARY_MULT!==constant) throw new Error('scenario override/local constant rule mismatch');
  S.advSecMult=constant;
  return {counts,cameraFloorKm:CAMERA_LIMITS.minAltitudeKm,snapshotSha:WORKBOOK_SNAPSHOT.meta.sha256,uprange:{primary:up.CAS_primary,secondary:up.CAS_secondary,total:up.CAS_total},downrange:{phase:coast.phaseClass,ignored:coast.ignoredFailureModes},returnPhase:{phase:ret.phaseClass,selected:ret.selectedFailureModes},bufferFactor:ASA.MODEL_BUFFER_FACTOR};
})()`);
console.log(JSON.stringify(receipt,null,2));
