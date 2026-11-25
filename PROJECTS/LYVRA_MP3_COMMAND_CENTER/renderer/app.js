'use strict';
const $=id=>document.getElementById(id),log=x=>{$('log').textContent=(JSON.stringify(x,null,2)+'\n'+$('log').textContent).slice(0,30000)},safe=fn=>async()=>{try{await fn()}catch(e){log({error:e.message})}};
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{for(const id of ['mp3','dj','restore'])$(id).hidden=id!==b.dataset.tab;$('title').textContent=b.textContent});
$('choose').onclick=safe(async()=>{for(const p of await cc.choose()){if([...$('files').options].some(o=>o.value===p))continue;const o=new Option(p,p,true,true);$('files').add(o)}});
$('folder').onclick=safe(async()=>{$('out').textContent=await cc.folder()||'Kein Ausgabeordner'});
$('stop').onclick=safe(()=>cc.stop());
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=safe(()=>cc.start({action:b.dataset.action,files:[...$('files').selectedOptions].map(o=>o.value),name:$('name').value,stream:Number($('stream').value),fields:{title:$('track').value,artist:$('artist').value,album:$('album').value},profile:$('profile').value,bitrate:Number($('bitrate').value),m3u:$('m3u').checked,mode:$('mode').value})));
cc.onEvent(x=>{log(x);const d=x.data;if(typeof d.fraction==='number')$('progress').value=d.fraction;else if(d.total>0)$('progress').value=d.done/d.total});
