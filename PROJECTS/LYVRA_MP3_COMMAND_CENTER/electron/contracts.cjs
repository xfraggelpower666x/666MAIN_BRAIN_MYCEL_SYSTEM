'use strict';
const path=require('node:path'),fs=require('node:fs');
const AUDIO=new Set(['.mp3','.wav','.flac','.ogg','.m4a','.aac','.aiff','.wma','.mp4','.mkv','.webm']);
function canonical(p){return fs.realpathSync(p);}
function output(dir,name,ext){
 if(typeof name!=='string'||!name||name!==path.basename(name)||/[<>:"/\\|?*\x00-\x1f]/.test(name)||name.endsWith('.')||name.endsWith(' ')||/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(name)||path.extname(name).toLowerCase()!==ext)throw Error('Ungültiger Ausgabename');
 const p=path.join(canonical(dir),name);try{fs.lstatSync(p);throw Error('Ausgabe existiert bereits')}catch(e){if(e.code!=='ENOENT')throw e;}return p;
}
function selected(p,set){const f=canonical(p);if(!set.has(f)||!fs.statSync(f).isFile()||!AUDIO.has(path.extname(f).toLowerCase()))throw Error('Quelle nicht autorisiert');return f;}
module.exports={AUDIO,canonical,output,selected};
