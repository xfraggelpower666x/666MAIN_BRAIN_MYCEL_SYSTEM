'use strict';
const overlay=new URLSearchParams(location.search).get('overlay')==='1';
if(overlay)document.body.classList.add('overlay');
let tab='d',last={status:'starting',disks:[]};
const $=id=>document.getElementById(id);
const fmt=n=>Number.isFinite(n)?(n/1024).toLocaleString('en-US',{maximumFractionDigits:1})+' KiB/s':'Unavailable';
function draw(){
  const root=$('drives');root.replaceChildren();
  $('notice').textContent=last.status==='ok'?'Live Python sampler · physical disk counters only':(last.error||'Sampler status: '+last.status);
  $('statustext').textContent=last.status+' · '+(last.timestamp||'no sample')+' · physical disks '+(last.disks||[]).length;
  if(!overlay)$('details').textContent=tab==='d'?'Live physical disk read/write counters. Hardware lock LEDs default OFF; no direct HID control.':
    'R19 candidate only: this tab awaits parity migration from the R18 source. Existing R18 remains the working reference.';
  for(const d of last.disks||[]){
    const name=String(d.name||'Unknown').slice(0,90),r=Number(d.read_bps)||0,w=Number(d.write_bps)||0;
    if(overlay){
      const item=document.createElement('div');item.className='mini';item.title=name+' · R '+fmt(r)+' · W '+fmt(w);
      const label=document.createElement('span');label.textContent=name;
      const led=document.createElement('span');led.className='led '+(w>4096?'write':r>4096?'read':'');
      item.append(label,led);root.append(item);continue;
    }
    const card=document.createElement('article');card.className='drive';
    const h=document.createElement('h2');h.textContent=name;card.append(h);
    const meters=document.createElement('div');meters.className='meters';
    for(const [label,value,kind] of [['READ',r,'read'],['WRITE',w,'write']]){
      const row=document.createElement('div');row.className='meter-row';
      const lbl=document.createElement('span');lbl.textContent=label;
      const track=document.createElement('div');track.className='track';
      const fill=document.createElement('div');fill.className='fill '+kind;fill.style.width=Math.min(100,100*value/(5*1024*1024))+'%';
      track.append(fill);const val=document.createElement('span');val.textContent=fmt(value);row.append(lbl,track,val);meters.append(row);
    }
    card.append(meters);root.append(card);
  }
}
for(const button of document.querySelectorAll('[data-tab]'))button.addEventListener('click',()=>{
  tab=button.dataset.tab;document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b===button));
  const headings={d:'DRIVE ACTIVITY · READ / WRITE',e:'DRIVE WORKSPACE · MIGRATION PENDING',a:'STORAGE · MIGRATION PENDING',b:'CLASSIC LED · MIGRATION PENDING',c:'TOOLS / RECOVERY · MIGRATION PENDING',status:'SYSTEM STATUS'};
  $('heading').textContent=headings[tab];draw();
});
$('overlay-toggle').addEventListener('click',()=>window.cyber.toggleOverlay());
window.cyber.onMetrics(data=>{last=data;draw();});
window.cyber.readMetrics().then(data=>{last=data;draw();}).catch(e=>{$('notice').textContent=String(e);});
