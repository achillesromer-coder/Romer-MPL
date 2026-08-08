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
let fetchCalls=0;
const context={console,document,window:windowObject,location:windowObject.location,navigator:{},fetch:async()=>{fetchCalls++;return{ok:false,status:503,json:async()=>({})};},
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
  const screening=calculateMPL({vehicle,site,phase:'UPRANGE',zone:'RURAL',failModes:[],isUprange:true});
  if(!Number.isFinite(screening.MPL_TOTAL)||screening.MPL_TOTAL<0)throw new Error('MPL total invalid');
  if(screening.MODEL_BUFFER!==Math.round(screening.MPL_TOTAL*1.10))throw new Error('model buffer mismatch');
  if(screening.evidenceBoundary?.impactIsopleth10e7!==false||screening.evidenceBoundary?.hvaSelection!=='ROMER_SCREENING_HEURISTIC')throw new Error('HVA evidence boundary missing');

  // Australian Space Agency MPL Methodology §6.1.3 parity:
  // one rounded primary casualty -> ceil(1*1.5)=2 secondary -> 3 total uprange.
  const unitVehicle={id:'TEST-UNIT',name:'Unit test vehicle',ac:1e6/ZONES.RURAL.popDensity};
  const uprange=calculateMPL({vehicle:unitVehicle,site,phase:'UPRANGE',zone:'RURAL',failModes:[],isUprange:true});
  if(uprange.CAS_primary!==1||uprange.CAS_secondary!==2||uprange.CAS_total!==3)throw new Error('uprange secondary-casualty parity failed');

  // Downrange/return excludes secondary effects and generic property/use/environment additions
  // under the controlled phase rule; specific HVA analysis remains a separate evidence surface.
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

  const workbook=vm.runInContext(`(()=>{
    S.site=SITES[0];S.vehicle=VEHICLES[0];S.transit=TRANSITS[0];S.failModeIds=[];S.achillesRef='BW5-001';
    simData.iipLat=S.site.lat+0.1;simData.iipLon=S.site.lon+0.1;
    const screening=calculateMPL({vehicle:S.vehicle,site:S.site,phase:'UPRANGE',zone:'RURAL',failModes:[],isUprange:true});
    S.lastRun={runId:'RMI-SMOKE-001',timestamp:'2026-08-09T00:00:00Z',failureTime:154,result:screening,pdfExported:false};
    const row=buildMissionLogRow(screening);
    if(JSON.stringify(Object.keys(row))!==JSON.stringify(MISSION_LOG_FIELDS))throw new Error('Mission_Log schema mismatch');
    if('Compliance' in row||'Model_Buffer' in row||'CorridorAssetCount' in row)throw new Error('non-canonical Mission_Log field leaked');
    if(row.LoggedToSheets!==false)throw new Error('unacknowledged browser write marked logged');
    if(!String(row.Notes).includes('SCREENING_BAND=')||!String(row.Notes).includes('MODEL_BUFFER_110_AUD='))throw new Error('Mission_Log provenance note incomplete');
    const screened=(screening.allAssets||[]).filter(a=>a.inCorridor===true);
    const expectedProp=Math.round(screened.reduce((sum,a)=>sum+Number(a.propExp||0),0));
    if(row.MPL_Property_Asset!==expectedProp)throw new Error('Mission_Log screened asset summary mismatch');

    const exposures=buildAssetExposureRows(screening,S.lastRun.runId);
    if(exposures.length!==(screening.allAssets||[]).length)throw new Error('Asset_Exposures row count mismatch');
    if(exposures.some(x=>JSON.stringify(Object.keys(x))!==JSON.stringify(ASSET_EXPOSURE_FIELDS)))throw new Error('Asset_Exposures schema mismatch');
    if(exposures.some(x=>typeof x.WithinScreeningHeuristic!=='boolean'))throw new Error('screening heuristic evidence flag missing');

    const w5=buildBridgeW5Update(screening);
    if(JSON.stringify(Object.keys(w5))!==JSON.stringify(BRIDGE_W5_UPDATE_FIELDS))throw new Error('BRIDGE_W5_Targets schema mismatch');
    if(!String(w5.MPL_Screening_Band).includes('BAND'))throw new Error('W5 screening band missing');
    const bridge=buildMplAchillesBridgeRow(screening);
    if(JSON.stringify(Object.keys(bridge))!==JSON.stringify(MPL_ACHILLES_BRIDGE_FIELDS))throw new Error('BRIDGE_MPL_to_ACHILLES schema mismatch');

    const receipt=prepareRunWorkbookWrites(screening);
    if(receipt.state!=='PENDING_OPERATOR_TRANSPORT')throw new Error('operator transport state mismatch');
    const tabs=receipt.writes.map(w=>w.tab);
    for(const tab of ['Mission_Log','Asset_Exposures','BRIDGE_MPL_to_ACHILLES','BRIDGE_W5_Targets'])if(!tabs.includes(tab))throw new Error('missing workbook write '+tab);

    const downrange=calculateMPL({vehicle:S.vehicle,site:S.site,phase:'DOWNRANGE',zone:'RURAL',failModes:[],isUprange:false});
    const downrow=buildMissionLogRow(downrange,{phase:'DOWNRANGE'});
    if(downrow.MPL_Property_Bounding!==0||downrow.MPL_LOU_GDP!==0||downrow.MPL_ENV_Bounding!==0)throw new Error('downrange Mission_Log bounding fields must be zero');
    return {missionFields:Object.keys(row).length,exposureRows:exposures.length,w5Fields:Object.keys(w5).length,bridgeFields:Object.keys(bridge).length,writeTabs:tabs,writeState:receipt.state};
  })()`,context,{timeout:10000});

  if(fetchCalls!==0)throw new Error(`workbook receipt preparation attempted ${fetchCalls} network write(s)`);
  console.log(JSON.stringify({result,contract,workbook,fetchCalls},null,2));
})().catch(error=>{console.error(error);process.exit(1);});
