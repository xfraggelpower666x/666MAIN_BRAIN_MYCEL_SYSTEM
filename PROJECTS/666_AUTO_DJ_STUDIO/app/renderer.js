'use strict';
const e=id=>document.getElementById(id);
let files=[],output=null,running=false;
const log=t=>{e('log').textContent+='\n'+String(t);e('log').scrollTop=e('log').scrollHeight;};
const state=v=>{running=v;e('start').disabled=v;e('cancel').disabled=!v;e('state').textContent=v?'RENDERING':'READY';};
async function add(paths){files=[...new Set([...files,...await window.autodj.validateFiles(paths)])];e('count').textContent=files.length;e('files').replaceChildren(...files.map(p=>{const item=document.createElement('li');item.textContent=p;return item;}));}
e('choose').onclick=async()=>add(await window.autodj.chooseFiles());
e('chooseDest').onclick=async()=>{const p=await window.autodj.chooseFolder();if(p){output=p;e('dest').textContent=p;}};
e('profile').onchange=()=>e('currentProfile').textContent=e('profile').value.toUpperCase();
const drop=e('drop');drop.onclick=()=>e('choose').click();
drop.onkeydown=event=>{if(event.key==='Enter')e('choose').click();};
drop.ondragover=ev=>{ev.preventDefault();drop.classList.add('over');};drop.ondragleave=()=>drop.classList.remove('over');
drop.ondrop=async ev=>{ev.preventDefault();drop.classList.remove('over');await add(window.autodj.pathsFromFiles(ev.dataTransfer.files));};
e('start').onclick=async()=>{if(running)return;if(!files.length||!output){log('Choose input files and output folder.');return;}e('log').textContent='';const r=await window.autodj.start({files,output,profile:e('profile').value,bitrate:Number(e('bitrate').value),export_m3u:e('exportM3u').checked,block_mode:e('blockMode').checked,split_mode:e('splitMode').value,target_minutes:Number(e('targetMinutes').value),target_tracks:Number(e('targetTracks').value),hardcore:e('hardcore').checked});if(r.ok)state(true);else log(r.error);};
e('cancel').onclick=async()=>{if(await window.autodj.cancel())log('Abort requested');};
window.autodj.onEvent(ev=>{if(ev.type==='finished'){state(false);log('Completed: '+ev.data.code);}else if(ev.type==='progress'){e('progress').textContent=(ev.data.done||0)+'/'+(ev.data.total||files.length);log(ev.data.message||JSON.stringify(ev.data));}else log(ev.data);});
