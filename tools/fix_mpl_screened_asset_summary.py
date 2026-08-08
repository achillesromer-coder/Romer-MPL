#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')
old="""  const assets=r.allAssets||r.nearbyAssets||[], nearest=assets.length?[...assets].sort((a,b)=>(a.dist_km??Infinity)-(b.dist_km??Infinity))[0]:null;
  const isUprange=String(r.phase||ctx.phase||'').toUpperCase()==='UPRANGE';
  const propAsset=assets.reduce((sum,a)=>sum+Number(a.propExp||0),0);
  const louAsset=assets.reduce((sum,a)=>sum+Number(a.louExp||0),0);
  const envAsset=assets.reduce((sum,a)=>sum+Number(a.envExp||0),0);"""
new="""  const assets=r.allAssets||r.nearbyAssets||[], nearest=assets.length?[...assets].sort((a,b)=>(a.dist_km??Infinity)-(b.dist_km??Infinity))[0]:null;
  const screenedAssets=assets.filter(a=>a.inCorridor===true);
  const isUprange=String(r.phase||ctx.phase||'').toUpperCase()==='UPRANGE';
  const propAsset=screenedAssets.reduce((sum,a)=>sum+Number(a.propExp||0),0);
  const louAsset=screenedAssets.reduce((sum,a)=>sum+Number(a.louExp||0),0);
  const envAsset=screenedAssets.reduce((sum,a)=>sum+Number(a.envExp||0),0);"""
if old in s:s=s.replace(old,new,1)
elif new not in s:raise SystemExit('screening asset summary anchor not found')
p.write_text(s,encoding='utf-8')
print('Mission_Log asset summary limited to WithinScreeningHeuristic assets')
