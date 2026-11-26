'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const defaults=Object.freeze({fullscreen:true,profile:'stream',bitrate:256,m3u:false,mode:'Both'});
function validate(x){if(!x||typeof x!=='object'||Array.isArray(x)||Object.keys(x).some(k=>!(k in defaults)))throw Error('Ungültige Einstellungen');const s={...defaults,...x};if(typeof s.fullscreen!=='boolean'||!['stream','dj','custom'].includes(s.profile)||![256,320].includes(s.bitrate)||typeof s.m3u!=='boolean'||!['Off','STFT','Wavelet','Both'].includes(s.mode))throw Error('Ungültige Einstellungen');return s}
function load(file){try{return validate(JSON.parse(fs.readFileSync(file,'utf8')))}catch(e){if(e.code==='ENOENT')return {...defaults};throw e}}
function save(file,value){const s=validate(value);fs.mkdirSync(path.dirname(file),{recursive:true});const tmp=file+'.'+crypto.randomUUID()+'.tmp';try{fs.writeFileSync(tmp,JSON.stringify(s,null,2)+'\n',{flag:'wx'});fs.renameSync(tmp,file)}finally{fs.rmSync(tmp,{force:true})}return s}
module.exports={defaults,validate,load,save};
