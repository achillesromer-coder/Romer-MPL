import { chromium } from 'playwright';

const url=process.env.CANDIDATE_URL||'http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true,args:['--enable-webgl','--ignore-gpu-blocklist','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const context=await browser.newContext({viewport:{width:1400,height:900}});
const page=await context.newPage();
const failures=[];
page.on('requestfailed',r=>failures.push({url:r.url(),error:r.failure()?.errorText||'unknown'}));
await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
await page.waitForFunction(()=>typeof S!=='undefined'&&document.getElementById('app')?.classList.contains('live'),null,{timeout:25000});

// Prepare the same finite result state used by the public result action, then render it so the UI control is exercised.
await page.evaluate(()=>{
  S.site=SITES[0];S.vehicle=VEHICLES[0];S.transit=TRANSITS[0];S.failModeIds=[];S.achillesRef='BW5-001';
  simData.iipLat=S.site.lat+0.1;simData.iipLon=S.site.lon+0.1;
  const result=calculateMPL({vehicle:S.vehicle,site:S.site,phase:'UPRANGE',zone:'RURAL',failModes:[],isUprange:true});
  S.lastRun={runId:'RMI-BROWSER-WRITE-001',timestamp:new Date().toISOString(),failureTime:154,result,pdfExported:false};
  showMPLResults(result,simData);
});
await page.waitForTimeout(250);

const button=page.getByRole('button',{name:'Prepare Workbook Write',exact:true}).first();
if(await button.count()!==1)throw new Error('Prepare Workbook Write control missing from rendered result surface');
await button.click({timeout:6000});
await page.waitForTimeout(150);
const receipt=await page.evaluate(()=>({
  state:S.lastWriteReceipt?.state,
  tabs:S.lastWriteReceipt?.writes?.map(w=>w.tab)||[],
  missionKeys:Object.keys(S.lastWriteReceipt?.writes?.find(w=>w.tab==='Mission_Log')?.row||{}),
  exposureKeys:Object.keys(S.lastWriteReceipt?.writes?.find(w=>w.tab==='Asset_Exposures')?.rows?.[0]||{}),
  w5Keys:Object.keys(S.lastWriteReceipt?.writes?.find(w=>w.tab==='BRIDGE_W5_Targets')?.data||{}),
  bridgeKeys:Object.keys(S.lastWriteReceipt?.writes?.find(w=>w.tab==='BRIDGE_MPL_to_ACHILLES')?.row||{}),
  expectedMission:[...MISSION_LOG_FIELDS],expectedExposure:[...ASSET_EXPOSURE_FIELDS],expectedW5:[...BRIDGE_W5_UPDATE_FIELDS],expectedBridge:[...MPL_ACHILLES_BRIDGE_FIELDS],
  toast:document.getElementById('toast')?.textContent||'',
}));

const equal=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
if(receipt.state!=='PENDING_OPERATOR_TRANSPORT')throw new Error(`unexpected write state: ${receipt.state}`);
for(const tab of ['Mission_Log','Asset_Exposures','BRIDGE_MPL_to_ACHILLES','BRIDGE_W5_Targets'])if(!receipt.tabs.includes(tab))throw new Error(`missing write tab: ${tab}`);
if(!equal(receipt.missionKeys,receipt.expectedMission))throw new Error('Mission_Log browser payload schema mismatch');
if(!equal(receipt.exposureKeys,receipt.expectedExposure))throw new Error('Asset_Exposures browser payload schema mismatch');
if(!equal(receipt.w5Keys,receipt.expectedW5))throw new Error('BRIDGE_W5_Targets browser payload schema mismatch');
if(!equal(receipt.bridgeKeys,receipt.expectedBridge))throw new Error('BRIDGE_MPL_to_ACHILLES browser payload schema mismatch');
if(!/operator transport required/i.test(receipt.toast))throw new Error(`write receipt toast missing transport boundary: ${receipt.toast}`);
const appsScriptFailures=failures.filter(x=>/script\.google\.com|googleusercontent\.com/.test(x.url));
if(appsScriptFailures.length)throw new Error(`write control attempted Apps Script network call: ${JSON.stringify(appsScriptFailures)}`);

console.log(JSON.stringify({status:'PASS',receipt,appsScriptFailures},null,2));
await browser.close();
