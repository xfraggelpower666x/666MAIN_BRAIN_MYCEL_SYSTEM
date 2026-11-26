'use strict';
const fs=require('node:fs'),path=require('node:path');
function locate(root,env=process.env,platform=process.platform,packaged=false){
 const suffix=platform==='win32'?'.exe':'';
 function resolve(name,override,relative){
  if(env[override]){if(!path.isAbsolute(env[override])||!fs.statSync(env[override]).isFile())throw Error('Ungültiger Runtime-Pfad: '+override);return env[override]}
  const local=path.join(root,'runtime',...relative,name+suffix);
  if(fs.existsSync(local)&&fs.statSync(local).isFile())return local;
  if(packaged)throw Error('Portable Runtime fehlt: '+local);
  return name;
 }
 return {python:resolve('python','LYVRA_PYTHON',['python']),ffmpeg:resolve('ffmpeg','LYVRA_FFMPEG',['ffmpeg']),ffprobe:resolve('ffprobe','LYVRA_FFPROBE',['ffmpeg'])};
}
module.exports={locate};
