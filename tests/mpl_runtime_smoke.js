const fs=require('fs');
const vm=require('vm');

const html=fs.readFileSync(process.argv[2]||'index.html','utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
const code=scripts.at(-1);
if(!code)throw new Error('Inline application script not found');

const noop=()=>{};
function element(){
  return new Proxy({style:{},dataset:{},children:[],textContent:'',innerHTML:'',value:'',checked:false,
    classList:{add:noop,remove:noop,toggle:noop,contains:()=>false},appendChild:noop,remove:noop,setAttribute:noop,getAttribute:()=>null,
    getBoundingClientRect:()=>({width:1200,height:750,left:0,top:0}),getContext:()=>new Proxy({},{get:()=>noop}),parentElement:null},
    {get:(target,key)=>key in target?target[key]:noop,set:(target,key,value)=>(target[key]=value,true)});
}
const elements=new Map();
const document={documentElement:{outerHTML:html},body:element(),
  getElementById:id=>{if(!elements.has(id))elements.set(id,element());return elements.get(id);},
  querySelectorAll:()=>[],querySelector:()=>null,createElement:()=>element(),addEventListener:noop};
const windowObject={addEventListener:noop,removeEventListener:noop,innerWidth:1500,innerHeight:900,devicePixelRatio:1,
  location:{hash:'',href:'https://example.test'},history:{replaceState:noop},open:noop,matchMedia:()=>({matches:false,addEventListener:noop,removeEventListener:noop})};
const context={console,document,window:windowObject,location:windowObject.location,navigator:{},fetch:async()=>({ok:false,status:503,json:async()=>({})}),
  localStorage:{getItem:()=>null,setItem:noop},sessionStorage:{getItem:()=>null,setItem:noop},setTimeout:()=>0,clearTimeout:noop,setInterval:()=>0,clearInterval:noop,
  requestAnimationFrame:()=>0,cancelAnimationFrame:noop,AbortSignal:{timeout:()=>({})},confirm:()=>false,URL,TextEncoder,crypto:require('crypto').webcrypto,
  Blob:global.Blob,performance:{now:()=>0},ResizeObserver:class{observe(){}disconnect(){}},Image:class{},FileReader:class{}};
context.globalThis=context;
vm.createContext(context);
vm.runInContext(code,context,{timeout:10000});

const result=vm.runInContext(`(()=>{
  if(MODEL_META.releaseStage!=='PRE_RELEASE')throw new Error('pre-release stage receipt missing');
  if(MODEL_META.dataMode!=='CONTROLLED_EMBEDDED_SNAPSHOT')throw new Error('controlled snapshot mode missing');
  if(typeof modelVersion!=='undefined')throw new Error('legacy modelVersion symbol leaked');
  const vehicle=VEHICLES[0],site=SITES[0];
  const screening=calculateMPL({vehicle,site,phase:'ascent',zone:'RURAL',failModes:[],isUprange:true});
  if(!Number.isFinite(screening.MPL_TOTAL)||screening.MPL_TOTAL<0)throw new Error('MPL total invalid');
  if(screening.MODEL_BUFFER!==Math.round(screening.MPL_TOTAL*1.10))throw new Error('model buffer mismatch');
  if(screening.evidenceBoundary?.impactIsopleth10e7!==false||screening.evidenceBoundary?.hvaSelection!=='ROMER_SCREENING_HEURISTIC')throw new Error('HVA evidence boundary missing');

  // ASA MPL Methodology §6.1.3 sample parity: one rounded primary casualty -> ceil(1*1.5)=2 secondary -> 3 total uprange.
  const unitVehicle={id:'TEST-UNIT',name:'Unit test vehicle',ac:1e6/ZONES.RURAL.popDensity};
  const uprange=calculateMPL({vehicle:unitVehicle,site,phase:'UPRANGE',zone:'RURAL',failModes:[],isUprange:true});
  if(uprange.CAS_primary!==1||uprange.CAS_secondary!==2||uprange.CAS_total!==3)throw new Error('uprange secondary-casualty parity failed');

  // Downrange/return excludes secondary effects and generic property/use/environment additions under the controlled phase rule.
  const downrange=calculateMPL({vehicle:unitVehicle,site,phase:'DOWNRANGE',zone:'RURAL',failModes:[],isUprange:false});
  if(downrange.CAS_secondary!==0)throw new Error('downrange secondary casualties must be zero');
  if(downrange.MPL_PD!==0||downrange.MPL_LOU!==0||downrange.MPL_ENV!==0)throw new Error('downrange generic non-casualty additions must be zero');
  return {screening:{mpl:screening.MPL_TOTAL,buffer:screening.MODEL_BUFFER,band:screening.compliance},uprange:{primary:uprange.CAS_primary,secondary:uprange.CAS_secondary,total:uprange.CAS_total},downrange:{secondary:downrange.CAS_secondary,pd:downrange.MPL_PD,lou:downrange.MPL_LOU,env:downrange.MPL_ENV}};
})()`,context,{timeout:10000});

(async()=>{
  await vm.runInContext('loadSheets()',context,{timeout:10000});
  const contract=vm.runInContext(`({sites:S.sites.length,vehicles:S.vehicles.length,fmodes:S.fmodes.length,assets:HVA_LIBRARY.length,mode:MODEL_META.dataMode,tabs:Object.keys(MODEL_META.dataTabs),sheetsOk:S.sheetsOk,bridge:ACHILLES_BRIDGE.length})`,context,{timeout:10000});
  if(contract.mode!=='CONTROLLED_EMBEDDED_SNAPSHOT'||contract.tabs.length!==10||contract.sheetsOk!==true)throw new Error('controlled snapshot receipt failed');
  if(!contract.sites||!contract.vehicles||!contract.fmodes||!contract.assets||!contract.bridge)throw new Error('embedded canonical datasets missing');
  console.log(JSON.stringify({result,contract},null,2));
})().catch(error=>{console.error(error);process.exit(1);});
