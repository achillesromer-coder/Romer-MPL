from pathlib import Path

INDEX = Path("index.html")
PROBE = Path("tests/browser_globe_probe.mjs")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source match, found {count}")
    return text.replace(old, new, 1)


def harden_index() -> None:
    source = INDEX.read_text(encoding="utf-8")

    if "logarithmicDepthBuffer:true" in source and "pinchDistance" in source:
        print("index.html already contains camera hardening")
        return

    source = replace_once(
        source,
        """#globe-canvas {\n  width: 100%; height: 100%;\n  background: radial-gradient(ellipse at 38% 42%, #0a1624 0%, #040a12 55%, #020508 100%);\n}""",
        """#globe-canvas {\n  width: 100%; height: 100%;\n  display: block;\n  touch-action: none;\n  background: radial-gradient(ellipse at 38% 42%, #0a1624 0%, #040a12 55%, #020508 100%);\n}""",
        "globe canvas interaction surface",
    )

    source = replace_once(
        source,
        "cameraAltitudeKm: 10000, drag: false, autoRot: true, showAtmo: true, hovSat: null,",
        "cameraAltitudeKm: finiteNumber(WORKBOOK_SNAPSHOT.config.DEFAULT_CAMERA_ALTITUDE_KM,10000), drag: false, autoRot: true, showAtmo: true, hovSat: null,",
        "initial camera altitude",
    )

    source = replace_once(
        source,
        """const EARTH_RADIUS_KM = 6371.0;\nconst CAMERA_LIMITS = Object.freeze({\n  minAltitudeKm: 1,\n  maxAltitudeKm: 40000,\n  defaultAltitudeKm: 10000,\n  siteFocusAltitudeKm: 180,\n  zoomFactor: 1.18,\n});""",
        """const EARTH_RADIUS_KM = 6371.0;\n// Camera limits are canonical workbook display controls. The 1 km floor is a Römer\n// rendering/collision invariant, not an ASA/MPL regulatory altitude threshold.\nconst CAMERA_LIMITS = Object.freeze({\n  minAltitudeKm: finiteNumber(WORKBOOK_SNAPSHOT.config.MIN_CAMERA_ALTITUDE_KM,1),\n  maxAltitudeKm: finiteNumber(WORKBOOK_SNAPSHOT.config.MAX_CAMERA_ALTITUDE_KM,40000),\n  defaultAltitudeKm: finiteNumber(WORKBOOK_SNAPSHOT.config.DEFAULT_CAMERA_ALTITUDE_KM,10000),\n  siteFocusAltitudeKm: finiteNumber(WORKBOOK_SNAPSHOT.config.SITE_FOCUS_ALTITUDE_KM,180),\n  zoomFactor: finiteNumber(WORKBOOK_SNAPSHOT.config.CAMERA_ZOOM_FACTOR,1.18),\n});""",
        "workbook camera controls",
    )

    source = replace_once(
        source,
        "renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,powerPreference:'high-performance',preserveDrawingBuffer:false});",
        """renderer=new THREE.WebGLRenderer({\n    canvas, antialias:true, alpha:true, powerPreference:'high-performance',\n    preserveDrawingBuffer:false, logarithmicDepthBuffer:true\n  });""",
        "globe renderer depth precision",
    )

    source = replace_once(
        source,
        """  canvas.addEventListener('touchstart',e=>{S.drag=true;S.autoRot=false;px=e.touches[0].clientX;py=e.touches[0].clientY;},{passive:true});\n  canvas.addEventListener('touchmove',e=>{\n    if(!S.drag)return;\n    const dx=(e.touches[0].clientX-px)*0.005, dy=(e.touches[0].clientY-py)*0.005;\n    globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));\n    userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));\n    px=e.touches[0].clientX;py=e.touches[0].clientY;\n  },{passive:true});\n  canvas.addEventListener('touchend',()=>S.drag=false);""",
        """  let pinchDistance=0, pinchAltitude=0;\n  const touchDistance=e=>{\n    if(e.touches.length<2)return 0;\n    return Math.hypot(e.touches[1].clientX-e.touches[0].clientX,e.touches[1].clientY-e.touches[0].clientY);\n  };\n  canvas.addEventListener('touchstart',e=>{\n    S.autoRot=false;\n    if(e.touches.length>=2){\n      S.drag=false;\n      pinchDistance=touchDistance(e);\n      pinchAltitude=S.cameraAltitudeKm;\n      return;\n    }\n    S.drag=true; px=e.touches[0].clientX; py=e.touches[0].clientY;\n  },{passive:true});\n  canvas.addEventListener('touchmove',e=>{\n    if(e.touches.length>=2){\n      e.preventDefault();\n      const distance=touchDistance(e);\n      if(pinchDistance>0&&distance>0)setCameraAltitudeKm(pinchAltitude*(pinchDistance/distance));\n      return;\n    }\n    if(!S.drag||!e.touches.length)return;\n    const dx=(e.touches[0].clientX-px)*0.005, dy=(e.touches[0].clientY-py)*0.005;\n    globe.rotation.y+=dx;globe.rotation.x=Math.max(-1.2,Math.min(1.2,globe.rotation.x+dy));\n    userDragY+=dx;userDragX=Math.max(-1.2,Math.min(1.2,userDragX+dy));\n    px=e.touches[0].clientX;py=e.touches[0].clientY;\n  },{passive:false});\n  canvas.addEventListener('touchend',e=>{\n    pinchDistance=0; pinchAltitude=0;\n    S.drag=e.touches.length===1;\n    if(S.drag){px=e.touches[0].clientX;py=e.touches[0].clientY;}\n  });""",
        "touch pinch altitude control",
    )

    source = source.replace(
        "UPRANGE_IA_M2:    3450000,  // §6.1.2.2; minimum 3.45 km² uprange overlay area unless the 10^-7 isopleth is larger.",
        "UPRANGE_IA_M2:    3450000,  // Methodology §6.2.3.2–6.2.3.3; 3.45 km² default impact area, with hazard-analysis isopleth geometry governing where larger.",
    )
    source = source.replace(
        "/* ─── ACHILLES: wire simReentry to actually trigger a re-entry sim ─── */",
        "/* ─── Satellite-to-return scenario handoff ─── */",
    )

    INDEX.write_text(source, encoding="utf-8")
    print("hardened index.html")


def harden_probe() -> None:
    source = PROBE.read_text(encoding="utf-8")
    if "touch-pinch-zoom-floor" in source:
        print("browser probe already contains camera hardening checks")
        return

    source = replace_once(
        source,
        """    if(!(renderer.info?.render?.calls>0)) throw new Error('renderer has not produced draw calls');\n    if(document.title!=='Römer MPL Platform — Pre-release') throw new Error(`unexpected title ${document.title}`);""",
        """    if(!(renderer.info?.render?.calls>0)) throw new Error('renderer has not produced draw calls');\n    if(renderer.capabilities?.logarithmicDepthBuffer!==true) throw new Error('globe renderer is not using logarithmic depth buffering');\n    if(document.title!=='Römer MPL Platform — Pre-release') throw new Error(`unexpected title ${document.title}`);""",
        "browser depth-buffer assertion",
    )

    source = replace_once(
        source,
        """    resetGlobe(); if(S.cameraAltitudeKm!==10000)throw new Error('reset altitude mismatch');\n    return {floorKm:min,radialKm:radialAlt,maxSurfaceLayerKm:maxSurface,resetKm:S.cameraAltitudeKm};\n  }));""",
        """    resetGlobe();\n    if(S.cameraAltitudeKm!==finiteNumber(WORKBOOK_SNAPSHOT.config.DEFAULT_CAMERA_ALTITUDE_KM,10000))throw new Error('reset altitude mismatch');\n    if(CAMERA_LIMITS.minAltitudeKm!==finiteNumber(WORKBOOK_SNAPSHOT.config.MIN_CAMERA_ALTITUDE_KM,1))throw new Error('minimum camera altitude not sourced from workbook snapshot');\n    if(CAMERA_LIMITS.maxAltitudeKm!==finiteNumber(WORKBOOK_SNAPSHOT.config.MAX_CAMERA_ALTITUDE_KM,40000))throw new Error('maximum camera altitude not sourced from workbook snapshot');\n    return {floorKm:min,radialKm:radialAlt,maxSurfaceLayerKm:maxSurface,resetKm:S.cameraAltitudeKm,limits:CAMERA_LIMITS};\n  }));""",
        "browser workbook-camera assertion",
    )

    source = replace_once(
        source,
        "  await run('view-switching-object-orbit',async()=>{",
        """  await run('touch-pinch-zoom-floor',()=>page.evaluate(()=>{\n    const canvas=document.getElementById('globe-canvas');\n    if(!canvas)throw new Error('globe canvas missing');\n    const dispatch=(type,points)=>{\n      const event=new Event(type,{bubbles:true,cancelable:true});\n      Object.defineProperty(event,'touches',{value:points.map(([clientX,clientY])=>({clientX,clientY}))});\n      canvas.dispatchEvent(event);\n    };\n    setCameraAltitudeKm(100);\n    dispatch('touchstart',[[100,100],[200,100]]);\n    dispatch('touchmove',[[50,100],[250,100]]);\n    if(Math.abs(S.cameraAltitudeKm-50)>0.001)throw new Error(`pinch zoom did not halve altitude: ${S.cameraAltitudeKm}`);\n    for(let i=0;i<12;i++){\n      dispatch('touchstart',[[100,100],[200,100]]);\n      dispatch('touchmove',[[0,100],[300,100]]);\n    }\n    if(S.cameraAltitudeKm<CAMERA_LIMITS.minAltitudeKm||camera.position.length()<radiusAtAltitudeKm(CAMERA_LIMITS.minAltitudeKm))throw new Error('pinch zoom penetrated Earth hard surface');\n    dispatch('touchend',[]);\n    resetGlobe();\n    return {pinchSupported:true,floorKm:CAMERA_LIMITS.minAltitudeKm};\n  }));\n\n  await run('view-switching-object-orbit',async()=>{""",
        "browser pinch regression",
    )

    PROBE.write_text(source, encoding="utf-8")
    print("hardened browser probe")


if __name__ == "__main__":
    harden_index()
    harden_probe()
