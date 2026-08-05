const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync(process.argv[2] || 'index.html', 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const code = scripts.at(-1);
if (!code) throw new Error('Inline application script not found');

const noop = () => {};
function element() {
  return new Proxy({
    style: {}, dataset: {}, children: [], textContent: '', innerHTML: '', value: '', checked: false,
    classList: { add: noop, remove: noop, toggle: noop, contains: () => false },
    appendChild: noop, remove: noop, setAttribute: noop, getAttribute: () => null,
    getBoundingClientRect: () => ({ width: 1200, height: 750, left: 0, top: 0 }),
    getContext: () => new Proxy({}, { get: () => noop }), parentElement: null,
  }, { get: (target, key) => key in target ? target[key] : noop, set: (target, key, value) => (target[key] = value, true) });
}
const elements = new Map();
const document = {
  documentElement: { outerHTML: html }, body: element(),
  getElementById: id => { if (!elements.has(id)) elements.set(id, element()); return elements.get(id); },
  querySelectorAll: () => [], querySelector: () => null, createElement: () => element(), addEventListener: noop,
};

const rows = {
  Launch_Sites: [{ SiteID:'LS900', SiteName:'Canonical Live Site', ShortName:'LIVE', CountryCode:'AUS', ActiveStatus:true, ShowInSelector:true, Latitude_dd:-20, Longitude_dd:140, NominalAzimuth_deg:90 }],
  Vehicles: [{ VehicleID:'V900', DisplayName:'Canonical Vehicle', Class:'Test', ActiveStatus:true, ShowInSelector:true, MassLiftoff_kg:1000, CasualtyArea_m2:100, Stages:1 }],
  MPL_Constants: [{ ConstantID:'MC-001', Value_AUD:7000000 }],
  GDP_Table: [{ CountryCode:'AUS', GDPPerCapita_USD:70000 }],
  Population_Zones: [{ ZoneID:'P900', ZoneName:'Live Zone', CountryCode:'AUS', RasterType:'RURAL', Latitude_dd:-20, Longitude_dd:140, RadiusKm:10, PopDensity_per_km2:1, GDPperCapita_USD:70000 }],
  Failure_Modes: [{ FailureModeID:'FM-900', FailureModeName:'Live Failure', Category:'Test', CasualtyAreaMultiplier:1, EnvironmentalMultiplier:1 }],
  MPL_Config: [{ ConfigID:'CF-020', Value:true }],
  Operators: [{ OperatorID:'OP-001', OperatorName:'Live Operator', ShortCode:'LO', ActiveStatus:true }],
  High_Value_Assets: [{ AssetID:'HVA900', AssetName:'Live Asset', AssetType:'Space Infrastructure', CountryCode:'AUS', ActiveStatus:true, ShowOnGlobe:true, Latitude_dd:-20.1, Longitude_dd:140.1, FootprintArea_m2:1000, PropertyValuePerM2:100, RevenuePerM2:10, TimeOutOfUse_months:1, EnvCleanupCost_USD:1000, ContainsToxicMaterials:false }],
  BRIDGE_W5_Targets: [{ BridgeID:'BW5-900', TargetName:'Live Target' }],
};
const fetch = async (_url, options = {}) => {
  const body = JSON.parse(options.body || '{}');
  return { ok: true, status: 200, json: async () => ({ ok: true, rows: rows[body.tab] || [] }) };
};
const windowObject = { addEventListener:noop, removeEventListener:noop, innerWidth:1500, innerHeight:900, devicePixelRatio:1, location:{hash:'',href:'https://example.test'}, history:{replaceState:noop}, open:noop };
const context = {
  console, document, window:windowObject, location:windowObject.location, navigator:{}, fetch,
  localStorage:{getItem:()=>null,setItem:noop}, sessionStorage:{getItem:()=>null,setItem:noop},
  setTimeout:()=>0, clearTimeout:noop, setInterval:()=>0, clearInterval:noop,
  requestAnimationFrame:()=>0, cancelAnimationFrame:noop, AbortSignal:{timeout:()=>({})},
  confirm:()=>false, URL, TextEncoder, crypto:require('crypto').webcrypto, Blob:global.Blob,
  performance:{now:()=>0}, ResizeObserver:class{observe(){} disconnect(){}}, Image:class{}, FileReader:class{},
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(code, context, { timeout: 10000 });

const calculation = vm.runInContext(`(() => {
  const vehicle=VEHICLES[0], site=SITES.find(s=>s.id==='LS005')||SITES[0];
  const result=calculateMPL({vehicle,site,phase:'UPRANGE',zone:'RURAL',failModes:['FM-001'],isUprange:true});
  if(!Number.isFinite(result.MPL_TOTAL)||result.MPL_TOTAL<=0) throw new Error('MPL total invalid');
  if(!Array.isArray(result.allAssets)||!result.allAssets.length) throw new Error('Asset exposure missing');
  if(!String(result.compliance).includes('SCREENING')) throw new Error('Screening classification missing');
  if(result.modelVersion!=='0.2.0') throw new Error('Model receipt missing');
  return {mpl:result.MPL_TOTAL,assets:result.allAssets.length,band:result.compliance};
})()`, context, { timeout: 10000 });

(async () => {
  const contract = await vm.runInContext(`loadSheets().then(()=>({
    sites:S.sites.map(x=>x.id), vehicles:S.vehicles.map(x=>x.id), fmodes:S.fmodes.map(x=>x.id),
    assets:HVA_LIBRARY.map(x=>x.id), mode:MODEL_META.dataMode, tabs:Object.keys(MODEL_META.dataTabs),
    casualtyValue:ASA.CASUALTY_VALUE, bridge:ACHILLES_BRIDGE.some(x=>x.id==='BW5-900')
  }))`, context, { timeout: 10000 });
  if(contract.sites[0]!=='LS900' || contract.vehicles[0]!=='V900' || contract.fmodes[0]!=='FM-900' || contract.assets[0]!=='HVA900') throw new Error('Canonical data replacement failed');
  if(contract.mode!=='LIVE_SHEETS' || contract.tabs.length!==10 || contract.casualtyValue!==7000000 || !contract.bridge) throw new Error('Live data receipt failed');
  console.log(JSON.stringify({ calculation, contract }, null, 2));
})().catch(error => { console.error(error); process.exit(1); });
