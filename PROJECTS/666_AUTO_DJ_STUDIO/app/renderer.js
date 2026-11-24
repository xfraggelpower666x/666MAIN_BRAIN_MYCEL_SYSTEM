const el=id=>document.getElementById(id);
let files=[],output=null,coversFolder=null,running=false;
function log(message){el('log').textContent+='\n'+String(message);el('log').scrollTop=el('log').scrollHeight;}
function setRunning(value){running=value;el('start').disabled=value;el('abort').disabled=!value;el('status').textContent=value?'RENDERING':'READY';}
async function add(paths){const resolved=await window.autodj.validateFiles(paths);files=[...new Set([...files,...resolved])];el('count').textContent=files.length;el('files').replaceChildren(...files.map(file=>{const li=document.createElement('li');li.textContent=file;return li;}));}
el('choose').onclick=async()=>add(await window.autodj.chooseFiles());
el('folder').onclick=async()=>{const selected=await window.autodj.chooseFolder();if(selected){output=selected;el('output').textContent=selected;}};
el('coversFolder').onclick=async()=>{const selected=await window.autodj.chooseFolder();if(selected){coversFolder=selected;el('coversPath').textContent=selected;}};
el('profile').onchange=()=>{el('liveProfile').textContent=el('profile').value.toUpperCase();};
const drop=el('drop');drop.onclick=()=>el('choose').click();drop.onkeydown=e=>{if(e.key==='Enter')el('choose').click();};
drop.ondragover=e=>{e.preventDefault();drop.classList.add('over');};drop.ondragleave=()=>drop.classList.remove('over');drop.ondrop=async e=>{e.preventDefault();drop.classList.remove('over');await add(window.autodj.pathsFromFiles(e.dataTransfer.files));};
el('start').onclick=async()=>{if(running)return;if(!files.length||!output){log('Select files and output folder first.');return;}el('log').textContent='';const response=await window.autodj.start({files,output,profile:el('profile').value,bitrate:Number(el('bitrate').value),block_mode:el('blockMode').checked,split_mode:el('splitMode').value,target_minutes:Number(el('targetMinutes').value),target_tracks:Number(el('targetTracks').value),hardcore:el('hardcore').checked,export_m3u:el('exportM3u').checked,write_metadata:el('writeMetadata').checked,rotate_covers:el('rotateCovers').checked,cover_dir:coversFolder,export_stream_ready:el('streamReady').checked});if(response.ok)setRunning(true);else log(response.error);};
el('abort').onclick=async()=>{if(await window.autodj.cancel())log('Abort requested.');};
window.autodj.onEvent(event=>{if(event.type==='finished'){setRunning(false);log('EXIT CODE '+event.data.code);}else if(event.type==='progress'){if(Number.isInteger(event.data.done))el('progress').textContent=event.data.done+'/'+event.data.total;log(event.data.message||JSON.stringify(event.data));}else log(event.data);});
