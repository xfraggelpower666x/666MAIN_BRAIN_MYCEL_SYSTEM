'use strict';
const fs=require('node:fs'),path=require('node:path');
const required=Object.freeze({mp:'mp3/ELECTRON_CANDIDATE/engine_bridge.py',media:'mp3/L.Y.V.R.A._MP3_MANAGER/media_tools.py',dj:'dj/666_AUTO_DJ_STUDIO/engine/worker.py',restore:'restore/Restoration-Lab-main/realtime.py',reference:'restore/Restoration-Lab-main/reference_engine.py',audio:'restore/Restoration-Lab-main/audio_input.py',boot:'boot/666_UNIVERSAL_PYTHON_ELECTRON_BUILDKIT_R01/electron/renderer/assets/bootscreen-1920x1080.webp'});
function resolveLayout(root){
 const diagnostics=[];
 for(const mode of ['originals','imports']){
  const base=path.join(root,mode),files=Object.fromEntries(Object.entries(required).map(([k,v])=>[k,path.join(base,v)]));
  const missing=Object.entries(files).filter(([,p])=>{try{return !fs.statSync(p).isFile()}catch{return true}}).map(([k])=>k);
  if(!missing.length)return {mode,base,...files};
  diagnostics.push(mode+': '+missing.join(', '));
 }
 throw Error('Unvollständiger Quellbestand: '+diagnostics.join('; '));
}
module.exports={required,resolveLayout};
