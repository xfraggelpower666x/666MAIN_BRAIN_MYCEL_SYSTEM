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
function bindingActive(binding,rate){
  if(!rate||!binding||!['read','write','either'].includes(binding.mode))return false;
  const threshold=Number(binding.threshold_kib)*1024;
  if(!Number.isFinite(threshold)||threshold<0)return false;
  const read=typeof rate.read_bps==='number'&&Number.isFinite(rate.read_bps)&&rate.read_bps>threshold;
  const write=typeof rate.write_bps==='number'&&Number.isFinite(rate.write_bps)&&rate.write_bps>threshold;
  return binding.mode==='read'?read:binding.mode==='write'?write:read||write;
}
function drawD(root){
  const dev=Array.isArray(last.physical)?last.physical:[];
  const p=create('div','control-card');p.append(create('h2',null,'PHYSISCHE DATENTRAEGER · CAPS/NUM/SCROLL VORSCHAU'));
  p.append(create('p','state-line','Nur optische Vorschau. Keine Tastatur- oder HID-Steuerung.'));
  const grid=create('div','control-grid');
  for(const key of ['caps','num','scroll']){
    // Do not mutate the authoritative saved binding when a physical device is unplugged.
    const conf={...(last.bindings?.[key]||bindings[key])}, ids=dev.map(d=>d.id);
    const displayDevice=ids.includes(conf.device)?conf.device:(ids.includes('_total')?'_total':(ids[0]||''));
    const d=dev.find(v=>v.id===conf.device);
    const on=bindingActive(conf,d);
    const card=create('div','control-card');card.append(create('h2',null,key.toUpperCase()+' · '+(on?'VORSCHAU AN':'AUS')));
    const save=async(device,mode,threshold)=>{
      const result=await window.cyber.setVisualBinding(key,device,mode,threshold);
      if(result?.ok){
        if(!last.bindings)last.bindings={};
        last.bindings[key]={device,mode,threshold_kib:threshold};
        $('notice').textContent=key.toUpperCase()+' Mapping gespeichert';
      }else{
        $('notice').textContent=result?.error||'Mapping konnte nicht gespeichert werden';
      }
      if(!grid.contains(document.activeElement))draw();
    };
    card.append(dropdown(dev.map(x=>[x.id,x.id]),displayDevice,v=>save(v,conf.mode,Number(conf.threshold_kib??4))));
    card.append(dropdown(modes.map(x=>[x,x]),conf.mode,v=>save(conf.device,v,Number(conf.threshold_kib??4))));
    const t=create('input');t.type='number';t.min='0';t.max='1048576';t.step='0.5';t.value=String(conf.threshold_kib??4);
    t.setAttribute('aria-label',key+' Schwellwert KiB/s');
    t.addEventListener('change',()=>save(conf.device,conf.mode,Number(t.value)));
    card.append(create('span',null,'Schwelle KiB/s: '),t);
    grid.append(card);
  }
  p.append(grid);$('controls').append(p);
  for(const d of dev){const card=create('article','drive');card.append(create('h2',null,d.id));
    const m=create('div','meters');m.append(meter('READ',d.read_bps,'read'),meter('WRITE',d.write_bps,'write'));
    card.append(m);root.append(card);}
}
function drawE(root){
  const panel=create('div','control-card');
  panel.append(create('h2',null,'E · LOGISCHE VOLUMES / USB / TRAY / OVERLAY'));
  const settings=last.settings||{},over=settings.overlay||{};
  panel.append(create('p',null,'Overlay: '));
  const layout=dropdown([['vertical','Untereinander'],['horizontal','Nebeneinander'],['minimal','Minimal: Buchstabe + LED']],over.layout||'vertical',async value=>{
    const result=await window.cyber.setOverlayLayout(value);
    $('notice').textContent=result.ok?'Layout gespeichert; naechstes Messbild abwarten':(result.error||'Fehler');
  });
  panel.append(layout);
  panel.append(create('p','state-line','LED '+(settings.led_hold_ms??'?')+' ms · Ruhe '+(settings.led_quiet_ms??'?')+' ms · Schwellwert '+(settings.activity_threshold_bps??'?')+' B/s'));
  $('controls').append(panel);
  for(const d of last.volumes||[]){
    const card=create('article','drive');
    card.append(create('h2',null,(d.letter||'?')+' · '+(d.label||'Unbenannt')));
    const meters=create('div','meters');meters.append(meter('READ',d.read_bps,'read'),meter('WRITE',d.write_bps,'write'));card.append(meters);
    card.append(create('div','drive-meta','Volume: '+String(d.id||'?')));
    card.append(create('div','drive-meta','Dateisystem: '+(d.filesystem||'?')+' · '+(d.measurement||'nicht messbar')));
    const settingsRow=create('div','target-options');
    for(const target of ['tray','overlay']){
      const lbl=create('label');
      const checkbox=create('input');checkbox.type='checkbox';checkbox.checked=Boolean(d.targets?.[target]);
      checkbox.addEventListener('change',async ()=>{
        const enabled=checkbox.checked;checkbox.disabled=true;
        try{
          const result=await window.cyber.setDriveVisibility(String(d.id),target,enabled);
          if(!result.ok)checkbox.checked=!enabled;
          $('notice').textContent=result.ok?'Gespeichert: '+d.letter+' '+target:(result.error||'Speichern fehlgeschlagen');
        }catch(err){
          checkbox.checked=!enabled;
          $('notice').textContent='IPC nicht verfuegbar';
        }finally{checkbox.disabled=false;}
      });
      lbl.append(checkbox,create('span',null,target==='tray'?'Tray':'Overlay'));settingsRow.append(lbl);
    }
    card.append(settingsRow);root.append(card);
  }
}
function drawA(root){
  const capacity=Array.isArray(last.capacity)?last.capacity:[];
  const issues=last.capacity_errors||{};
  for(const v of capacity){
    const card=create('article','drive');
    card.append(create('h2',null,v.mountpoint+' · '+(v.filesystem||'Volume')));
    const size=Number(v.total_bytes)||0,free=Number(v.free_bytes)||0,used=Number(v.used_bytes)||0;
    card.append(create('div','drive-meta','Gesamt: '+(size/(1024**3)).toFixed(1)+' GiB · Frei: '+(free/(1024**3)).toFixed(1)+' GiB · Belegt: '+(used/(1024**3)).toFixed(1)+' GiB'));
    const track=create('div','track'),fill=create('div','fill '+(v.status==='critical'?'write':'read'));
    fill.style.width=Math.max(0,Math.min(100,Number(v.used_percent)||0))+'%';track.append(fill);
    card.append(track,create('p','state-line','Belegung '+v.used_percent+'% · '+String(v.status||'unavailable').toUpperCase()));
    root.append(card);
  }
  for(const [drive,error] of Object.entries(issues)){
    root.append(create('div','control-card',drive+': '+error));
  }
  if(!capacity.length&&!Object.keys(issues).length)root.append(create('div','control-card','Keine Kapazitätsmessung verfügbar.'));
}
function drawB(root){
  const p=create('div','control-card');
  p.append(create('h2',null,'B · CLASSIC SSD / LOCK-ANZEIGE (LESEMODUS)'));
  p.append(create('p','state-line','Originale R18-Classic-Farbvorschau. Hardware-Schaltfunktion ist nicht aktiviert.'));
  const preview=last.classic_preview;
  if(preview){
    const sample=last.physical?.find(x=>x.id===preview.device);
    const indicator=create('div','classic-indicator','●');
    indicator.style.color=typeof preview.indicator_color==='string'?preview.indicator_color:'#394354';
    p.append(indicator);
    if(sample)p.append(create('div','drive-meta','READ '+fmt(sample.read_bps)+' · WRITE '+fmt(sample.write_bps)));
  }else p.append(create('p','state-line','Classic-Signal derzeit nicht verfügbar.'));
  root.append(p);
}
function drawC(root){
  const p=create('div','control-card');
  p.append(create('h2',null,'C · TOOL-DIAGNOSE / RECOVERY — ENTWICKLERSEITIG'));
  p.append(create('p',null,'R18 besitzt separate Tools für Diagnose, Setup, Updates und Python-Recovery. Diese Aktionen bleiben vollständig im zentralen Windows-Batch und werden nicht in das Endbenutzer-Tool eingebaut.'));
  p.append(create('p','state-line','Kein Installations- oder Update-Befehl aus Electron.'));
  root.append(p);
}
function drawStatus(root){
  const x=last.overview;
  if(!x){root.append(create('div','control-card','Systemmessung nicht verfügbar: '+String(last.overview_error||'?')));return;}
  const p=create('div','control-card');
  p.append(create('h2',null,'R18 · SYSTEMÜBERSICHT'));
  for(const [label,value,unit] of [['CPU',x.cpu_pct,'%'],['RAM',x.memory_pct,'%'],['DISK READ',x.disk_read_bps,'bytes'],['DISK WRITE',x.disk_write_bps,'bytes'],['NETWORK RX',x.rx_bps,'bytes'],['NETWORK TX',x.tx_bps,'bytes']]){
    p.append(create('div','drive-meta',label+' · '+(unit==='%'?Number(value).toFixed(1)+'%':fmt(value))));
  }
  root.append(p);
}
function drawOverlay(root){
  for(const d of last.volumes||[]){if(!d.targets?.overlay)continue;
    const item=create('div','mini');item.title=[d.letter,d.label,d.id,'R '+fmt(d.read_bps),'W '+fmt(d.write_bps),d.filesystem].join(' · ');
    item.append(create('span',null,d.letter||'?'));
    // R18 BicolorActivity determines pulse color, not a naive rate threshold.
    const color=d.led_color==='#FF4FD8'?'write':d.led_color==='#35E0FF'?'read':'';
    const led=create('span','led '+color);item.append(led);root.append(item);
    if(color){
      // R18 sampled pulse is 180ms by default; visual expiry is independent
      // of the 500ms telemetry interval. The backend remains authoritative.
      const hold=Math.max(40,Math.min(2000,Number(last.settings?.led_hold_ms)||180));
      setTimeout(()=>{if(led.isConnected)led.className='led';},hold);
    }}
}
function draw(){
  const root=$('drives'),controls=$('controls');
  const active=document.activeElement;
  if(!overlay && controls.contains(active) && (active.tagName==='INPUT'||active.tagName==='SELECT'))return;
  root.replaceChildren();controls.replaceChildren();
  $('notice').textContent=last.status==='ok'?'R18 live · D physische Devices / E logische Volumes':(last.error||'Sampler: '+last.status);
  $('statustext').textContent=last.status+' · '+(last.timestamp||'kein Sample')+' · '+(last.volumes||[]).length+' Volumes';
  if(overlay){drawOverlay(root);return;}
  const headings={d:'D · PHYSICAL DRIVE LED MAPPING',e:'E · DRIVE WORKSPACE',a:'A · VOLUME CAPACITY',b:'B · CLASSIC · SAFE PREVIEW',c:'C · TOOLS / RECOVERY · EXTERNAL',status:'SYSTEM STATUS'};
  $('heading').textContent=headings[tab];
  $('details').textContent=tab==='d'?'D verwendet den R18 DiskActivitySampler; sichere Mapping-Einstellungen werden separat dauerhaft gespeichert, ohne Hardwarezugriff.':tab==='e'?'E zeigt R18 Volume-GUID, PDH und gespeicherte Auswahl.': 'R18 Daten werden lesend genutzt. Funktionen mit Systemaenderungen bleiben in den externen Windows-Tools.';
  if(tab==='d')drawD(root);else if(tab==='e')drawE(root);
  else if(tab==='a')drawA(root);
  else if(tab==='b')drawB(root);
  else if(tab==='c')drawC(root);
  else if(tab==='status')drawStatus(root);
}
for(const b of document.querySelectorAll('[data-tab]'))b.addEventListener('click',()=>{tab=b.dataset.tab;document.querySelectorAll('[data-tab]').forEach(x=>x.classList.toggle('active',x===b));draw();});
$('controls').addEventListener('focusout',()=>queueMicrotask(()=>{if(!$('controls').contains(document.activeElement))draw();}));
$('settings-toggle').addEventListener('click',()=>window.cyber.openSettings());
$('overlay-toggle').addEventListener('click',()=>window.cyber.toggleOverlay());
window.cyber.onMetrics(data=>{last=data;draw();});
window.cyber.readMetrics().then(data=>{last=data;draw();}).catch(e=>{$('notice').textContent=String(e);});
