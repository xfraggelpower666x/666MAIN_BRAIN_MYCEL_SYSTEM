"""Offline, dependency-free 666TDH UI. Buttons ONLY copy verified trigger strings."""

from __future__ import annotations

from html import escape
import json


def render_html(view: dict) -> str:
    data = json.dumps(view, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    title = escape(view["title"], quote=True)
    return ('''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>666TDH · '''+title+'''</title><style>
:root{color-scheme:dark;font-family:system-ui,Arial,sans-serif;background:#0b0e18;color:#e9edf7}
body{margin:0 auto;max-width:1100px;padding:24px}header{margin-bottom:22px}
h1{margin:6px 0;color:#7be8ff}small{color:#b3bccc}.panel{background:#131b2a;border:1px solid #344457;border-radius:14px;padding:16px;margin:12px 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px}
button{color:#e8efff;background:#17273b;border:1px solid #31546b;border-radius:10px;padding:12px;cursor:pointer;text-align:left}
button:focus-visible{outline:2px solid #fa72df}button:hover{background:#243d56}
.tag{color:#f5d089}.muted{color:#afbacb}.status{padding:8px 0;color:#81e3cb}
</style></head><body><header><small>666TDH · Repo-nativer Current</small><h1 id="title"></h1><div class="muted" id="basis"></div></header>
<div class="panel"><strong>Intelligente Ansichten</strong><div id="sections" class="grid"></div></div>
<div class="panel"><strong>Menü – Trigger kopieren</strong><p class="muted">Die Schaltflächen kopieren nur den angegebenen Befehl. Sie führen keinen Chat-Turn oder System-Write aus.</p><div id="menu" class="grid"></div></div>
<div class="panel"><strong>Begleit-Daemon (beratend)</strong><p id="daemon"></p><p id="evidence" class="muted"></p><button id="daemon-toggle" type="button">Begleiter lokal ausblenden</button></div>
<div id="feedback" role="status" class="status"></div>
<script type="application/json" id="tdh-data">'''+data+'''</script><script>
'use strict';const data=JSON.parse(document.getElementById('tdh-data').textContent);
const byId=id=>document.getElementById(id);const el=(tag,text)=>{const x=document.createElement(tag);x.textContent=text;return x};
byId('title').textContent=data.title;byId('basis').textContent='Release '+data.native_release+' · '+data.scope+' · Host-Abnahme: '+data.host_acceptance;
for(const section of data.sections){const b=el('button',section.title);b.type='button';b.addEventListener('click',()=>{byId('feedback').textContent='Ansicht gewählt: '+section.title+' (lokale Auswahl)'});byId('sections').append(b)}
for(const item of data.menu){const b=el('button',item.title+' · '+item.command);b.type='button';b.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(item.command);byId('feedback').textContent='Kopiert: '+item.command}catch(_){byId('feedback').textContent='Bitte manuell kopieren: '+item.command}});byId('menu').append(b)}
byId('daemon').textContent=data.companion.next_safe_action;byId('evidence').textContent='Prüfung: '+data.companion.countercheck+' · Quelle: '+data.companion.evidence.join(', ');
let shown=true;byId('daemon-toggle').addEventListener('click',()=>{shown=!shown;byId('daemon').hidden=!shown;byId('evidence').hidden=!shown;byId('daemon-toggle').textContent=shown?'Begleiter lokal ausblenden':'Begleiter lokal einblenden'});
</script></body></html>''')
