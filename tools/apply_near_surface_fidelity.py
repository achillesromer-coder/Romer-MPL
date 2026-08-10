from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="""    const blob=await response.blob();if(!/^image\\//i.test(blob.type))throw new Error(`GIBS returned ${blob.type||'non-image content'}`);const bitmap=await createImageBitmap(blob);if(seq!==nearSurfaceImageryState.requestSeq){bitmap.close?.();return false;}
    const tex=new THREE.Texture(bitmap);tex.needsUpdate=true;tex.minFilter=THREE.LinearMipMapLinearFilter;tex.magFilter=THREE.LinearFilter;tex.anisotropy=renderer?renderer.capabilities.getMaxAnisotropy():16;tex.userData={bitmap,source:NEAR_SURFACE_IMAGERY.source,resolutionM:NEAR_SURFACE_IMAGERY.sourceResolutionM};if('encoding' in tex)tex.encoding=THREE.sRGBEncoding;"""
new="""    const blob=await response.blob();if(!/^image\\//i.test(blob.type))throw new Error(`GIBS returned ${blob.type||'non-image content'}`);
    const objectUrl=URL.createObjectURL(blob),image=await new Promise((resolve,reject)=>{const img=new Image();img.decoding='async';img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('GIBS image decode failed'));img.src=objectUrl;});
    URL.revokeObjectURL(objectUrl);if(seq!==nearSurfaceImageryState.requestSeq)return false;
    const tex=new THREE.Texture(image);tex.needsUpdate=true;tex.minFilter=THREE.LinearMipmapLinearFilter||THREE.LinearMipMapLinearFilter;tex.magFilter=THREE.LinearFilter;tex.anisotropy=renderer?renderer.capabilities.getMaxAnisotropy():16;tex.userData={source:NEAR_SURFACE_IMAGERY.source,resolutionM:NEAR_SURFACE_IMAGERY.sourceResolutionM};if('colorSpace' in tex&&THREE.SRGBColorSpace)tex.colorSpace=THREE.SRGBColorSpace;else if('encoding' in tex&&THREE.sRGBEncoding)tex.encoding=THREE.sRGBEncoding;"""
if old not in s:
    raise SystemExit('expected createImageBitmap decoder not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('updated near-surface image decoder')