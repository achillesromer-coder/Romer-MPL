#!/usr/bin/env python3
from pathlib import Path
import sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'index.html')
s=p.read_text(encoding='utf-8')

# The Earth is the depth-authoritative hard surface. Atmosphere, data overlays and markers are
# separate layers and must never make the camera appear to pass through the planet.
if "const GLOBE_SURFACE_MODE='HARD_OPAQUE_EARTH';" not in s:
    anchor="const EARTH_RADIUS_KM=6371.0088,CAMERA_MIN_ALTITUDE_KM=1,CAMERA_MAX_ALTITUDE_KM=40000,CAMERA_INITIAL_ALTITUDE_KM=11500,CAMERA_SITE_ALTITUDE_KM=80,SURFACE_PROXIMITY_KM=150;"
    if anchor not in s:raise SystemExit('camera constants anchor missing')
    s=s.replace(anchor,anchor+"\nconst GLOBE_SURFACE_MODE='HARD_OPAQUE_EARTH';",1)

old="""  globe=new THREE.Mesh(new THREE.SphereGeometry(1,128,128),new THREE.MeshPhongMaterial({
    map:mapTex,specularMap:mapTex,specular:new THREE.Color(0x2a4060),shininess:35,
    emissive:new THREE.Color(0x040810),emissiveIntensity:0.25,
  }));
  scene.add(globe);"""
new="""  globe=new THREE.Mesh(new THREE.SphereGeometry(1,128,128),new THREE.MeshPhongMaterial({
    map:mapTex,specularMap:mapTex,specular:new THREE.Color(0x2a4060),shininess:35,
    emissive:new THREE.Color(0x040810),emissiveIntensity:0.25,
    transparent:false,opacity:1,depthTest:true,depthWrite:true,side:THREE.FrontSide,
  }));
  globe.userData.surfaceMode=GLOBE_SURFACE_MODE;
  scene.add(globe);"""
if old in s:s=s.replace(old,new,1)
elif 'globe.userData.surfaceMode=GLOBE_SURFACE_MODE;' not in s:raise SystemExit('globe material anchor missing')

for marker in ['transparent:false','opacity:1','depthTest:true','depthWrite:true','side:THREE.FrontSide','surfaceMode=GLOBE_SURFACE_MODE']:
    if marker not in s:raise SystemExit('hard-surface invariant missing: '+marker)
p.write_text(s,encoding='utf-8')
print('hard opaque Earth surface invariant applied')
