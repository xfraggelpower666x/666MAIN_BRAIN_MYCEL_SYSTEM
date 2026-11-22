'use strict';
const overlay=new URLSearchParams(location.search).get('overlay')==='1';
if(overlay)document.body.classList.add('overlay');
let tab='d',last={status:'starting',volumes:[],physical:[]};
const $=id=>document.getElementById(id);
const fmt=n=>typeof n==='number'&&Number.isFinite(n)?(n/1024).toLocaleString('de-DE',{maximumFractionDigits:1})+' KiB/s':'nicht verfügbar';
function create(tag,cls,value){const e=document.createElement(tag);if(cls)e.className=cls;if(value!==undefined)e.textContent=String(value);return e;}
const modes=['off','read','write','either'];
const bindings={caps:{device:'_total',mode:'off'},num:{device:'_total',mode:'off'},scroll:{device:'_total',mode:'off'}};
function dropdown(items,value,changed){
  const e=create('select');for(const [key,label] of items){const o=create('option',null,label);o.value=key;e.append(o);}
  e.value=value;e.addEventListener('change',()=>changed(e.value));return e;
}
function meter(label,value,kind){
  const row=create('div','meter-row');row.append(create('span',null,label));
  const track=create('div','track'),fill=create('div','fill '+kind);
  fill.style.width=Math.min(100,Math.max(0,(value||0)/(5*1024*1024))*100)+'%';
  track.append(fill);row.append(track,create('span',null,fmt(value)));return row;
}
function drawD(root){
  const dev=Array.isArray(last.physical)?last.physical:[];
  const p=create('div','control-card');p.append(create('h2',null,'PHYSISCHE DATENTRAEGER · CAPS/NUM/SCROLL VORSCHAU'));
  p.append(create('p','state-line','Nur optische Vorschau. Keine Tastatur- oder HID-Steuerung.'));
  const grid=create('div','control-grid');
  for(const key of ['caps','num','scroll']){
    const conf=bindings[key], ids=dev.map(d=>d.id);
    if(!ids.includes(conf.device))conf.device=ids.includes('_total')?'_total':(ids[0]||'');
    const d=dev.find(v=>v.id===conf.device),threshold=last.settings?.activity_threshold_bps??4096;
    const on=Boolean(d&&conf.mode!=='off'&&(conf.mode==='read'?d.read_bps>threshold:conf.mode==='write'?d.write_bps>threshold:d.read_bps>threshold||d.write_bps>threshold));
    const card=create('div','control-card');card.append(create('h2',null,key.toUpperCase()+' · '+(on?'VORSCHAU AN':'AUS')));
    card.append(dropdown(dev.map(x=>[x.id,x.id]),conf.device,v=>{conf.device=v;draw();}));
    card.append(dropdown(modes.map(x=>[x,x]),conf.mode,v=>{conf.mode=v;draw();}));grid.append(card);
  }
  p.append(grid);$('controls').append(p);
  for(const d of dev){const card=create('article','drive');card.append(create('h2',null,d.id));
    const m=create('div','meters');m.append(meter('READ',d.read_bps,'read'),meter('WRITE',d.write_bps,'write'));
    card.append(m);root.append(card);}
}
function drawE(root){
  const panel=create('div','control-card');
  panel.append(create('h2',null,'LOGISCHE VOLUMES · USB-HOTPLUG · TRAY / OVERLAY STATUS'));
  panel.append(create('p','state-line','R18-Auswahl wird gelesen. Aenderungen am gespeicherten Workspace folgen als gesonderter, gepruefter Schritt.'));
  const settings=last.settings||{},o=settings.overlay||{};
  panel.append(create('p',null,'Overlay-Layout: '+(o.layout||'?')+' · Impuls: '+(settings.led_hold_ms??'?')+' ms · Ruhe: '+(settings.led_quiet_ms??'?')+' ms · Schwelle: '+(settings.activity_threshold_bps??'?')+' B/s'));
  $('controls').append(panel);
  for(const d of last.volumes||[]){
    const card=create('article','drive');card.append(create('h2',null,(d.letter||'?')+' · '+(d.label||'Unbenannt')));
    const m=create('div','meters');m.append(meter('READ',d.read_bps,'read'),meter('WRITE',d.write_bps,'write'));
    card.append(m);
    card.append(create('div','drive-meta','Volume-ID: '+String(d.id||'?')));
    card.append(create('div','drive-meta','Dateisystem: '+(d.filesystem||'?')+' · '+(d.measurement||'nicht messbar')+' · Tray '+(d.targets?.tray?'AN':'AUS')+' · Overlay '+(d.targets?.overlay?'AN':'AUS')));
    root.append(card);
  }
}
function drawOverlay(root){
  const threshold=last.settings?.activity_threshold_bps??4096;
  for(const d of last.volumes||[]){if(!d.targets?.overlay)continue;
    const item=create('div','mini');item.title=[d.letter,d.label,d.id,'R '+fmt(d.read_bps),'W '+fmt(d.write_bps),d.filesystem].join(' · ');
    item.append(create('span',null,d.letter||'?'));
    const color=d.write_bps!==null&&d.write_bps>threshold?'write':d.read_bps!==null&&d.read_bps>threshold?'read':'';
    item.append(create('span','led '+color));root.append(item);}
}
function draw(){
  const root=$('drives');root.replaceChildren();$('controls').replaceChildren();
  $('notice').textContent=last.status==='ok'?'R18 live · D physische Devices / E logische Volumes':(last.error||'Sampler: '+last.status);
  $('statustext').textContent=last.status+' · '+(last.timestamp||'kein Sample')+' · '+(last.volumes||[]).length+' Volumes';
  if(overlay){drawOverlay(root);return;}
  const headings={d:'D · PHYSICAL DRIVE LED MAPPING',e:'E · DRIVE WORKSPACE',a:'A · STORAGE · OFFEN',b:'B · CLASSIC · OFFEN',c:'C · TOOLS · OFFEN',status:'SYSTEM STATUS'};
  $('heading').textContent=headings[tab];
  $('details').textContent=tab==='d'?'D verwendet ausschliesslich den R18 DiskActivitySampler. LED-Mapping ist momentan Vorschau ohne Hardwarezugriff.':tab==='e'?'E zeigt R18 Volume-GUID, PDH und gespeicherte Auswahl.': 'Dieses R18-Funktionsmodul ist in Electron noch nicht uebernommen.';
  if(tab==='d')drawD(root);else if(tab==='e')drawE(root);
  else if(tab==='status')$('controls').append(create('div','control-card','Quelle: '+String(last.source||'?')+' · PDH-Volumes: '+(last.volumes||[]).length+' · Physische Datentraeger: '+(last.physical||[]).length));
}
for(const b of document.querySelectorAll('[data-tab]'))b.addEventListener('click',()=>{tab=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));draw();});
$('overlay-toggle').addEventListener('click',()=>window.cyber.toggleOverlay());
window.cyber.onMetrics(data=>{last=data;draw();});
window.cyber.readMetrics().then(data=>{last=data;draw();}).catch(e=>{$('notice').textContent=String(e);});
