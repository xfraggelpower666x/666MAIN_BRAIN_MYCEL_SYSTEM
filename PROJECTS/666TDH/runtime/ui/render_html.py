"""Offline-TDH-UI: echte lokale Ansichten; Trigger ausschließlich kopieren."""
from __future__ import annotations

from html import escape
import json


def render_html(view: dict) -> str:
    """Rendere ein Offline-Dashboard ohne externe Requests oder Autoritätswechsel."""
    data = (json.dumps(view, ensure_ascii=False)
            .replace("<", "\\u003c").replace(">", "\\u003e")
            .replace("&", "\\u0026"))
    title = escape(view["title"], quote=True)
    return ('''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>666TDH · '''+title+'''</title><style>
:root{color-scheme:dark;font-family:system-ui,Arial,sans-serif;background:#0b0e18;color:#e9edf7}
body{margin:0 auto;max-width:1100px;padding:24px}header{margin-bottom:22px}
h1{margin:6px 0;color:#7be8ff}small{color:#b3bccc}.panel{background:#131b2a;border:1px solid #344457;border-radius:14px;padding:16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
button{color:#e8efff;background:#17273b;border:1px solid #31546b;border-radius:10px;padding:12px;cursor:pointer;text-align:left}
button:focus-visible{outline:2px solid #fa72df}button:hover,button[aria-selected=true]{background:#243d56}
.tag{color:#f5d089}.muted{color:#afbacb}.status{padding:8px 0;color:#81e3cb}
#facts{padding-left:1.3rem}#facts li{padding:4px 0;overflow-wrap:anywhere}#copy-buffer{width:100%;box-sizing:border-box;background:#101927;color:#e8efff;border:1px solid #31546b;padding:10px;border-radius:8px}
@media(max-width:560px){body{padding:12px}.panel{padding:12px}.grid{grid-template-columns:1fr}}
</style></head><body><header><small>666TDH · Repo-nativer Current</small><h1 id="title"></h1><div class="muted" id="basis"></div></header>
<div class="panel"><strong>Intelligente Ansichten</strong><div id="sections" class="grid" role="tablist" aria-label="TDH-Ansichten"></div>
<section aria-label="Aktuelle Ansicht"><h2 id="view-title"></h2><p id="view-summary"></p><p class="tag" id="view-status"></p><ul id="facts"></ul><p class="muted" id="view-source"></p></section></div>
<div class="panel"><strong>Menü – Trigger kopieren</strong><p class="muted">Diese Befehle werden nur angezeigt und kopiert. Kein Child wird automatisch gestartet, keine Dateien geändert.</p><div id="menu" class="grid"></div>
<label for="copy-buffer">Befehl zum manuellen Kopieren</label><input id="copy-buffer" readonly value="" aria-label="Gewählter Befehl"></div>
<div class="panel"><strong>Begleit-Daemon (beratend)</strong><p id="daemon"></p><p id="evidence" class="muted"></p><div id="daemon-menu" class="grid"></div><button id="daemon-toggle" type="button">Begleiter lokal ausblenden</button></div>
<div id="feedback" role="status" aria-live="polite" class="status"></div>
<script type="application/json" id="tdh-data">'''+data+'''</script><script>
'use strict';const data=JSON.parse(document.getElementById('tdh-data').textContent);
const byId=id=>document.getElementById(id);const el=(tag,text)=>{const x=document.createElement(tag);x.textContent=text;return x};
byId('title').textContent=data.title;byId('basis').textContent='Release '+data.native_release+' · '+data.scope+' · Host-Abnahme: '+data.host_acceptance;
const selectSection=(section,id)=>{
 byId('view-title').textContent=section.title;byId('view-summary').textContent=section.summary;
 byId('view-status').textContent='Status: '+section.status;byId('view-source').textContent='Quelle: '+section.source;
 byId('facts').replaceChildren(...section.facts.map(f=>el('li',f)));
 for(const tab of byId('sections').querySelectorAll('[role=tab]'))tab.setAttribute('aria-selected',String(tab.dataset.view===id));
 byId('feedback').textContent='Ansicht gewählt: '+section.title;
};
for(const section of data.sections){const b=el('button',section.title);b.type='button';b.role='tab';b.dataset.view=section.id;b.setAttribute('aria-selected','false');b.addEventListener('click',()=>selectSection(section,section.id));byId('sections').append(b)}
if(data.sections.length)selectSection(data.sections[0],data.sections[0].id);
for(const item of data.menu){const b=el('button',item.title+' · '+item.command);b.type='button';b.addEventListener('click',async()=>{
 const buffer=byId('copy-buffer');buffer.value=item.command;buffer.focus();buffer.select();
 try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw new Error('clipboard-unavailable');
   await navigator.clipboard.writeText(item.command);byId('feedback').textContent='Kopiert: '+item.command}
 catch(_){byId('feedback').textContent='Befehl im Textfeld auswählen und manuell kopieren: '+item.command}
});byId('menu').append(b)}
for(const item of (data.daemon_menu||[])){
 const b=el('button',item.title+' · '+item.command);b.type='button';
 b.addEventListener('click',async()=>{
   const buffer=byId('copy-buffer');buffer.value=item.command;buffer.focus();buffer.select();
   try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw new Error('clipboard-unavailable');
     await navigator.clipboard.writeText(item.command);byId('feedback').textContent='Kopiert: '+item.command}
   catch(_){byId('feedback').textContent='Manuell kopieren: '+item.command}
 });byId('daemon-menu').append(b)
}
byId('daemon').textContent=data.companion.next_safe_action;
byId('evidence').textContent='Status: '+data.companion.state+' · Gegenprobe: '+data.companion.countercheck+' · Quellen: '+data.companion.evidence.join(', ');
let shown=true;byId('daemon-toggle').addEventListener('click',()=>{shown=!shown;byId('daemon').hidden=!shown;byId('evidence').hidden=!shown;byId('daemon-toggle').textContent=shown?'Begleiter lokal ausblenden':'Begleiter lokal einblenden'});
</script></body></html>''')
