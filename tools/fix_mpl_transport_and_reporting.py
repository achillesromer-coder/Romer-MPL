#!/usr/bin/env python3
"""Idempotent pre-release repair for reporting semantics and workbook write contracts.

The public GitHub Pages runtime is anonymous/static. It therefore builds exact workbook
payloads and durable local operator-write receipts instead of claiming that a cross-origin
Apps Script POST was acknowledged. The canonical workbook schemas are encoded explicitly
so source/test failures occur when the runtime drifts from the workbook contract.
"""
from pathlib import Path
import re,sys

p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')

# User-facing/export terminology: model screening bands, never regulatory PASS/FAIL claims.
s=s.replace('/* Compliance badge */','/* Model-check screening-band badge */')
s=s.replace('// Compliance badge','// Model-check screening-band badge')
s=s.replace("background:${r.compliance.includes('PASS')?'#e8f5ee':'#fff8e0'};",
            "background:${r.compliance.includes('LOWER')?'#e8f5ee':r.compliance.includes('UPPER')?'#fff0e0':'#fff8e0'};")
s=s.replace("color:${r.compliance.includes('PASS')?'#1a7a40':'#8a6010'};",
            "color:${r.compliance.includes('LOWER')?'#1a7a40':r.compliance.includes('UPPER')?'#a44a00':'#8a6010'};")
s=s.replace("border:1px solid ${r.compliance.includes('PASS')?'#a0d8b4':'#d4aa40'}",
            "border:1px solid ${r.compliance.includes('LOWER')?'#a0d8b4':r.compliance.includes('UPPER')?'#e3a06a':'#d4aa40'}")
s=s.replace("['RunID','Timestamp','Site','Vehicle','MPL_Total','Model_Buffer','CAS_Total','Compliance']",
            "['RunID','Timestamp','Site','Vehicle','MPL_Total','Model_Buffer','CAS_Total','Screening_Band']")
s=s.replace("'ENV','Compliance','TopHVA','ProxW'","'ENV','Screening_Band','TopHVA','ProxW'")

# Results/action labels accurately describe public-runtime capabilities.
s=s.replace('onclick="logMissionRun()">Log to Sheets</button>',
            'onclick="logMissionRun()">Prepare Workbook Write</button>')
s=s.replace('onclick="logBatchToSheets()" id="batch-log-btn" disabled style="font-size:11px;padding:5px 12px;">Log to Sheets</button>',
            'onclick="logBatchToSheets()" id="batch-log-btn" disabled style="font-size:11px;padding:5px 12px;">Prepare Workbook Write</button>')

# Replace the first run-logging block with one exact workbook-schema builder and an inspectable
# operator-side transport bundle. Anchor ends immediately before the W5 bridge section.
start=s.find('function logMissionRun(){')
end=s.find('// Write MPL result back to ACHILLES W5 bridge',start)
if start<0 or end<0:
    if 'const MISSION_LOG_FIELDS=Object.freeze([' not in s:
        raise SystemExit('Mission log block anchors not found')
else:
    replacement=r'''const MISSION_LOG_FIELDS=Object.freeze([
  'RunID','Timestamp','OperatorID','OperatorName','SiteID','SiteName','SiteLat','SiteLon','VehicleID','VehicleName',
  'TransitType','FailureMode','FailureTiming','FailureTime_Tplus_s','FlightPhase','IIP_Lat','IIP_Lon','ImpactZoneType',
  'ImpactZoneName','PopDensity_km2','Ac_m2','CAS_Primary','CAS_Secondary','CAS_Total','MPL_Casualties',
  'MPL_Property_Bounding','MPL_Property_Asset','MPL_Property_Used','MPL_LOU_GDP','MPL_LOU_Asset','MPL_LOU_Used',
  'MPL_ENV_Bounding','MPL_ENV_Asset','MPL_ENV_Used','MPL_TOTAL','CurrencyYear','NearestAssetID','NearestAssetKm',
  'RunStatus','LoggedToSheets','PDFExported','AchillesBridgeRef','Notes'
]);
const ASSET_EXPOSURE_FIELDS=Object.freeze(['ExposureID','RunID','AssetID','AssetName','DistFromIIP_km','WithinScreeningHeuristic','PropertyLoss_AUD','LossOfUse_AUD','EnvCleanup_AUD','TotalExposure_AUD','LastUpdated']);
const BRIDGE_W5_UPDATE_FIELDS=Object.freeze(['MPL_RunID','MPL_Screening_Band','MPL_Total_AUD','MPL_Model_Buffer_AUD','BridgeStatus','LastUpdated','UpdatedBy']);
const MPL_ACHILLES_BRIDGE_FIELDS=Object.freeze(['BridgeID','ACHILLESRowRef','MPL_RunID','MPL_Screening_Band','MPL_Total_AUD','MPL_Model_Buffer_AUD','MPL_Calc_Date','MPL_Method_Ref','LaunchSiteID','VehicleID','FlightPhase_Worst','CAS_Total_Worst','W6_UpdateRequired']);

function screeningBandCode(value){
  const text=String(value||'REVIEW').toUpperCase();
  if(text.includes('LOWER')) return 'LOWER_SCREENING_BAND';
  if(text.includes('UPPER')) return 'UPPER_REVIEW_BAND';
  if(text.includes('INTERMEDIATE')) return 'INTERMEDIATE_REVIEW_BAND';
  return 'REVIEW';
}
function exactSchemaObject(fields,data){
  return Object.fromEntries(fields.map(field=>[field,Object.prototype.hasOwnProperty.call(data,field)?data[field]:'']));
}
function buildMissionLogRow(r,ctx={}){
  const site=ctx.site||S.site||SITES[0], vehicle=ctx.vehicle||S.vehicle||VEHICLES[0], transit=ctx.transit||S.transit;
  const runId=ctx.runId||S.lastRun?.runId||`${getRunPrefix()}-${Date.now()}`;
  const timestamp=ctx.timestamp||S.lastRun?.timestamp||new Date().toISOString();
  const assets=r.allAssets||r.nearbyAssets||[], nearest=assets.length?[...assets].sort((a,b)=>(a.dist_km??Infinity)-(b.dist_km??Infinity))[0]:null;
  const isUprange=String(r.phase||ctx.phase||'').toUpperCase()==='UPRANGE';
  const propAsset=assets.reduce((sum,a)=>sum+Number(a.propExp||0),0);
  const louAsset=assets.reduce((sum,a)=>sum+Number(a.louExp||0),0);
  const envAsset=assets.reduce((sum,a)=>sum+Number(a.envExp||0),0);
  const band=screeningBandCode(r.compliance);
  const notes=[
    'PRE_RELEASE',`SCREENING_BAND=${band}`,`MODEL_BUFFER_110_AUD=${Math.round(r.MODEL_BUFFER||r.MPL_TOTAL*1.10)}`,
    `DATA_MODE=${MODEL_META.dataMode}`,`RUNTIME_HASH=${MODEL_META.runtimeHash}`,
    `HVA_SELECTION=${r.evidenceBoundary?.hvaSelection||'ROMER_SCREENING_HEURISTIC'}`,
    `IMPACT_ISOPLETH_1E-7=${r.evidenceBoundary?.impactIsopleth10e7?'SUPPLIED':'NOT_SUPPLIED'}`,
    ctx.note||''
  ].filter(Boolean).join(' | ');
  return exactSchemaObject(MISSION_LOG_FIELDS,{
    RunID:runId,Timestamp:timestamp,OperatorID:S.activeOperator?.id||'OP-001',OperatorName:S.activeOperator?.name||'N. Römer',
    SiteID:site?.id||'NOT PROVIDED',SiteName:site?.name||'NOT PROVIDED',SiteLat:site?.lat??'',SiteLon:site?.lon??'',
    VehicleID:vehicle?.id||'NOT PROVIDED',VehicleName:vehicle?.name||'NOT PROVIDED',TransitType:transit?.id||ctx.transitType||'NOT PROVIDED',
    FailureMode:ctx.failureMode||S.failModeIds?.join(',')||'NOT PROVIDED',FailureTiming:ctx.failureTiming||S.failMode||'NOT PROVIDED',
    FailureTime_Tplus_s:Number.isFinite(ctx.failureTime)?Number(ctx.failureTime.toFixed(1)):Number.isFinite(S.lastRun?.failureTime)?Number(S.lastRun.failureTime.toFixed(1)):'',
    FlightPhase:r.phase||ctx.phase||'NOT PROVIDED',IIP_Lat:Number.isFinite(ctx.iipLat)?Number(ctx.iipLat.toFixed(6)):Number.isFinite(simData?.iipLat)?Number(simData.iipLat.toFixed(6)):'',
    IIP_Lon:Number.isFinite(ctx.iipLon)?Number(ctx.iipLon.toFixed(6)):Number.isFinite(simData?.iipLon)?Number(simData.iipLon.toFixed(6)):'',
    ImpactZoneType:r.zone||ctx.zone||'NOT PROVIDED',ImpactZoneName:r.zoneData?.name||ctx.zoneName||'NOT PROVIDED',PopDensity_km2:r.Dpop??'',Ac_m2:Number.isFinite(r.Ac)?Math.round(r.Ac):'',
    CAS_Primary:r.CAS_primary??0,CAS_Secondary:r.CAS_secondary??0,CAS_Total:r.CAS_total??0,MPL_Casualties:Math.round(r.MPL_CAS||0),
    MPL_Property_Bounding:isUprange?Math.round((r.MPL_CAS||0)*ASA.PROPERTY_PCT):0,MPL_Property_Asset:Math.round(propAsset),MPL_Property_Used:Math.round(r.MPL_PD||0),
    MPL_LOU_GDP:isUprange?Math.round((r.CAS_total||0)*(GDP_TABLE[site?.cc]||GDP_TABLE.GLB)):0,MPL_LOU_Asset:Math.round(louAsset),MPL_LOU_Used:Math.round(r.MPL_LOU||0),
    MPL_ENV_Bounding:isUprange?Math.round(ASA.ENV_BOUNDING):0,MPL_ENV_Asset:Math.round(envAsset),MPL_ENV_Used:Math.round(r.MPL_ENV||0),MPL_TOTAL:Math.round(r.MPL_TOTAL||0),
    CurrencyYear:2024,NearestAssetID:nearest?.id||'',NearestAssetKm:nearest?.dist_km??'',RunStatus:'COMPLETE',LoggedToSheets:false,
    PDFExported:Boolean(S.lastRun?.pdfExported),AchillesBridgeRef:S.achillesRef||'',Notes:notes
  });
}
function buildAssetExposureRows(r,runId){
  const iipLat=Number(simData?.iipLat),iipLon=Number(simData?.iipLon),now=new Date().toISOString();
  return (r.allAssets||r.nearbyAssets||[]).map(a=>{
    const dist=Number.isFinite(iipLat)&&Number.isFinite(iipLon)?haversine(iipLat,iipLon,a.lat,a.lon):'';
    return exactSchemaObject(ASSET_EXPOSURE_FIELDS,{
      ExposureID:`${runId}-${a.id}`,RunID:runId,AssetID:a.id,AssetName:a.name,DistFromIIP_km:Number.isFinite(dist)?Number(dist.toFixed(3)):'',
      WithinScreeningHeuristic:Boolean(a.inCorridor),PropertyLoss_AUD:Math.round(a.propExp||0),LossOfUse_AUD:Math.round(a.louExp||0),
      EnvCleanup_AUD:Math.round(a.envExp||0),TotalExposure_AUD:Math.round((a.propExp||0)+(a.louExp||0)+(a.envExp||0)),LastUpdated:now
    });
  });
}
function buildBridgeW5Update(r){
  return exactSchemaObject(BRIDGE_W5_UPDATE_FIELDS,{
    MPL_RunID:S.lastRun?.runId||'',MPL_Screening_Band:screeningBandCode(r.compliance),MPL_Total_AUD:Math.round(r.MPL_TOTAL||0),
    MPL_Model_Buffer_AUD:Math.round(r.MODEL_BUFFER||r.MPL_TOTAL*1.10),BridgeStatus:'MPL_SCREENING_COMPLETE',LastUpdated:new Date().toISOString(),UpdatedBy:S.activeOperator?.id||'OP-001'
  });
}
function buildMplAchillesBridgeRow(r){
  const runId=S.lastRun?.runId||`${getRunPrefix()}-${Date.now()}`;
  return exactSchemaObject(MPL_ACHILLES_BRIDGE_FIELDS,{
    BridgeID:`MPL-${runId}`,ACHILLESRowRef:S.achillesRef||'',MPL_RunID:runId,MPL_Screening_Band:screeningBandCode(r.compliance),
    MPL_Total_AUD:Math.round(r.MPL_TOTAL||0),MPL_Model_Buffer_AUD:Math.round(r.MODEL_BUFFER||r.MPL_TOTAL*1.10),MPL_Calc_Date:new Date().toISOString(),
    MPL_Method_Ref:'ASA_MPL_2019_SCREENING',LaunchSiteID:S.site?.id||'',VehicleID:S.vehicle?.id||'',FlightPhase_Worst:r.phase||'',CAS_Total_Worst:r.CAS_total||0,
    W6_UpdateRequired:(r.allAssets||r.nearbyAssets||[]).length?'YES':'NO'
  });
}
function queueOperatorWriteBundle(writes,label='MPL workbook write'){
  const receipt={id:`WRITE-${Date.now()}`,state:'PENDING_OPERATOR_TRANSPORT',label,createdAt:new Date().toISOString(),operatorId:S.activeOperator?.id||'OP-001',writes};
  S.pendingWrites=Array.isArray(S.pendingWrites)?S.pendingWrites:[];S.pendingWrites.push(receipt);S.pendingWrites=S.pendingWrites.slice(-20);S.lastWriteReceipt=receipt;
  try{localStorage.setItem('romerMplPendingWrites',JSON.stringify(S.pendingWrites));}catch{}
  return receipt;
}
function prepareRunWorkbookWrites(r=S.lastRun?.result){
  if(!S.lastRun||!r){toast('No run data to prepare');return null;}
  const runId=S.lastRun.runId,missionRow=buildMissionLogRow(r),exposureRows=buildAssetExposureRows(r,runId);
  const writes=[
    {action:'append',tab:'Mission_Log',schema:MISSION_LOG_FIELDS,row:missionRow},
    {action:'batch_append',tab:'Asset_Exposures',schema:ASSET_EXPOSURE_FIELDS,rows:exposureRows},
    {action:'append',tab:'BRIDGE_MPL_to_ACHILLES',schema:MPL_ACHILLES_BRIDGE_FIELDS,row:buildMplAchillesBridgeRow(r)}
  ];
  if(S.achillesRef)writes.push({action:'update_bridge',tab:'BRIDGE_W5_Targets',bridgeId:S.achillesRef,schema:BRIDGE_W5_UPDATE_FIELDS,data:buildBridgeW5Update(r)});
  const receipt=queueOperatorWriteBundle(writes,'MPL run workbook write');
  S.lastRun.writeReceiptId=receipt.id;
  return receipt;
}
function logMissionRun(){
  const receipt=prepareRunWorkbookWrites();
  if(!receipt)return;
  toast(`Workbook write prepared — ${receipt.id} · operator transport required`);
  if(S.webhookUrl)dispatchWebhook(S.lastRun);
}

'''
    s=s[:start]+replacement+s[end:]

# W5 bridge is part of the prepared operator-write bundle; do not attempt an unverifiable cross-origin POST.
w5_start=s.find('// Write MPL result back to ACHILLES W5 bridge')
w5_end=s.find('// ACHILLES W6',w5_start)
if w5_start>=0 and w5_end>w5_start:
    s=s[:w5_start]+'''// W5 bridge updates are generated by buildBridgeW5Update() and queued with the operator-write bundle.\nfunction writeAchillesBridge(r){\n  if(!S.achillesRef)return null;\n  const receipt=queueOperatorWriteBundle([{action:'update_bridge',tab:'BRIDGE_W5_Targets',bridgeId:S.achillesRef,schema:BRIDGE_W5_UPDATE_FIELDS,data:buildBridgeW5Update(r)}],'ACHILLES W5 bridge write');\n  return receipt;\n}\n\n'''+s[w5_end:]

# Remove the later wrapper that redefined logMissionRun; webhook dispatch is integrated into the canonical function above.
wrap_start=s.find('/* Wire webhook into logMissionRun */')
wrap_end=s.find('/* ─── Mission Event Timeline',wrap_start)
if wrap_start>=0 and wrap_end>wrap_start:
    s=s[:wrap_start]+s[wrap_end:]

# Retain full calculation objects in batchResults so canonical Mission_Log rows can be prepared without recomputation drift.
s=s.replace("batchResults.push({label:item.label,site:item.site.short,vehicle:item.vehicle.name,zone:item.zone,failMode:item.failMode,",
            "batchResults.push({label:item.label,site:item.site.short,vehicle:item.vehicle.name,siteObj:item.site,vehicleObj:item.vehicle,result:r,zone:item.zone,failMode:item.failMode,")

# Replace batch cross-origin logger with schema-faithful operator-write bundle generation.
batch_start=s.find('async function logBatchToSheets() {')
batch_end=s.find('\nfunction openAI()',batch_start)
if batch_start>=0 and batch_end>batch_start:
    batch_func=r'''function logBatchToSheets(){
  if(!batchResults.length){toast('No batch results to prepare');return;}
  const now=new Date().toISOString();
  const missionRows=batchResults.map((item,index)=>buildMissionLogRow(item.result,{
    runId:`${getRunPrefix()}-BATCH-${Date.now()}-${String(index+1).padStart(3,'0')}`,timestamp:now,site:item.siteObj,vehicle:item.vehicleObj,
    transitType:'BATCH',failureMode:item.failMode,failureTiming:'BATCH',phase:item.result?.phase||'UPRANGE',zone:item.zone,note:`BATCH_SCENARIO=${item.label}`
  }));
  const writes=[{action:'batch_append',tab:'Mission_Log',schema:MISSION_LOG_FIELDS,rows:missionRows}];
  const receipt=queueOperatorWriteBundle(writes,'MPL batch workbook write');
  const btn=document.getElementById('batch-log-btn');if(btn)btn.textContent='Workbook Write Prepared';
  toast(`Batch workbook write prepared — ${receipt.id} · operator transport required`);
  return receipt;
}
'''
    s=s[:batch_start]+batch_func+s[batch_end:]

# Explicit source comments explain why public runtime does not issue Apps Script writes.
s=s.replace('/* Wire webhook into logMissionRun */','/* Webhook dispatch is integrated into the canonical write-preparation function. */')

# Contract checks: no duplicate logger, no undefined legacy transport helper, no PASS/FAIL report styling.
checks={
  'duplicate logMissionRun':len(re.findall(r'function\s+logMissionRun\s*\(',s))==1,
  'canonical mission fields':"const MISSION_LOG_FIELDS=Object.freeze([" in s,
  'canonical bridge field':"MPL_Screening_Band" in s,
  'legacy bridge field removed':"MPL_Compliance:" not in s,
  'undefined logToSheets removed':"logToSheets(data)" not in s,
  'PASS report styling removed':"r.compliance.includes('PASS')" not in s,
  'batch direct Apps Script write removed':"action:'batch_append', tab:'Mission_Log', rows" not in s,
}
failed=[name for name,ok in checks.items() if not ok]
if failed:raise SystemExit('transport/report invariant failed: '+', '.join(failed))

p.write_text(s,encoding='utf-8')
print('transport/reporting contracts aligned with canonical workbook schemas')
