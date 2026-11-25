// Separate, per-user application settings. No compiler/build-manager state is stored here.
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const DEFAULTS=Object.freeze({fullscreen:true,language:'de',theme:'dark'});
const MAX_BYTES=16384;
function validate(raw){
  if(raw===null || typeof raw!=='object' || Array.isArray(raw))throw new Error('Invalid settings object');
  const allowed=new Set(Object.keys(DEFAULTS));
  for(const key of Object.keys(raw))if(!allowed.has(key))throw new Error(`Unsupported setting: ${key}`);
  const s={...DEFAULTS,...raw};
  if(typeof s.fullscreen!=='boolean')throw new Error('fullscreen must be boolean');
  if(!['de','en'].includes(s.language))throw new Error('language not supported');
  if(!['dark','cyber'].includes(s.theme))throw new Error('theme not supported');
  return s;
}
function createStore(directory){
  if(typeof directory!=='string' || !directory)throw new Error('Settings directory required');
  const filename=path.join(directory,'settings.json');
  function load(){
    try{
      const stat=fs.statSync(filename);
      if(stat.size>MAX_BYTES)throw new Error('Settings file too large');
      return validate(JSON.parse(fs.readFileSync(filename,'utf8')));
    }catch(error){
      if(error.code==='ENOENT')return {...DEFAULTS};
      return {...DEFAULTS};
    }
  }
  function save(input){
    const next=validate(input);
    fs.mkdirSync(directory,{recursive:true});
    const tmp=path.join(directory,`settings.${process.pid}.${Date.now()}.tmp`);
    try{
      fs.writeFileSync(tmp,JSON.stringify(next,null,2)+'\n',{encoding:'utf8',flag:'wx',mode:0o600});
      if(process.platform==='win32' && fs.existsSync(filename)){
        const previous=filename+'.before-write';
        if(fs.existsSync(previous))fs.unlinkSync(previous);
        fs.renameSync(filename,previous);
        try{fs.renameSync(tmp,filename);fs.unlinkSync(previous)}
        catch(error){if(fs.existsSync(previous))fs.renameSync(previous,filename);throw error;}
      }else fs.renameSync(tmp,filename);
    }finally{if(fs.existsSync(tmp))fs.unlinkSync(tmp)}
    return next;
  }
  return {filename,load,save};
}
module.exports={DEFAULTS,validate,createStore};
