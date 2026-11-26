'use strict';
const $=id=>document.getElementById(id);
const api=window.catalog;
const state={queue:[],rows:[],selected:null,record:null,page:0,stats:null,archived:false,archivePage:0,multi:new Set()};
const categories={lyrics:'Lyrics',style_prompt:'Style Prompt',prompt:'Prompt',framework:'Framework',code:'Code',diverse:'Diverse'};
function node(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=String(text);return el}
function notice(txt,error=false){const flag=$('statusFlag');if(flag){flag.textContent=error?'● Fehler':'● Lokal';flag.setAttribute('aria-label',error?'Fehler bei letzter Aktion':'Lokale Datenbank');}const n=$('notice');n.textContent=txt;n.classList.remove('hidden');n.style.borderColor=error?'#ae536f':'#60577e';}
function error(e){notice(e?.message||String(e),true)}
async function task(fn){try{return await fn()}catch(e){error(e);return null}}
function tab(name){document.querySelectorAll('.view').forEach(e=>e.classList.toggle('active',e.id===name));document.querySelectorAll('.nav').forEach(e=>{const active=e.dataset.tab===name;e.classList.toggle('active',active);if(active)e.setAttribute('aria-current','page');else e.removeAttribute('aria-current')});$('pageTitle').textContent=({dashboard:'Control Dashboard',import:'Universal Import Center',browser:'Datenbankbrowser',analysis:'Lyrics Visual Intelligence',projects:'Projekt-Intelligence',archive:'Old Archive',system:'System & Dependencies'})[name];if(name==='browser')loadRows();if(name==='projects')loadProjectInsights();if(name==='system')checkTools();if(name==='archive')loadArchiveR07();}
document.querySelectorAll('.nav').forEach(b=>b.onclick=()=>tab(b.dataset.tab));document.querySelectorAll('[data-goto]').forEach(b=>b.onclick=()=>tab(b.dataset.goto));
async function refresh(){const s=await task(()=>api.status());if(!s)return;state.stats=s;$('mTotal').textContent=s.total.toLocaleString('de-DE');$('mArchived').textContent=s.archived.toLocaleString('de-DE');$('mImports').textContent=s.import_total.toLocaleString('de-DE');const counts={};s.projects.forEach(x=>counts[x.project]=(counts[x.project]||0)+x.count);$('mProjects').textContent=Object.keys(counts).length;const stat=$('projectStats');stat.replaceChildren();const max=Math.max(...Object.values(counts),1);Object.entries(counts).sort((a,b)=>b[1]-a[1]).forEach(([p,count])=>{const wrap=node('div','project-row');const head=node('div','project-name');head.append(node('span','',p),node('span','',count));const bar=node('div','bar');const inner=node('div','bar-inner');inner.style.width=100*count/max+'%';bar.append(inner);wrap.append(head,bar);stat.append(wrap)});if(!stat.children.length)stat.textContent='Noch keine Datensätze importiert.';const hist=$('importHistory');hist.replaceChildren();s.imports.forEach(x=>{const r=node('div','hist');r.append(node('span','',x.source_name),node('span',x.status==='done'?'ok':'fail',`${x.status} · +${x.inserted}`));hist.append(r)});if(!s.imports.length)hist.textContent='Noch keine Importläufe.';const select=$('filterProject');const old=select.value;select.replaceChildren(new Option('Alle Projekte',''));Object.keys(counts).sort().forEach(p=>select.add(new Option(p,p)));select.value=old;}
function enqueue(paths,{replace=false}={}){let set=new Set(replace?[]:state.queue);paths.forEach(p=>{if(p)set.add(p)});state.queue=[...set];const q=$('queue');q.replaceChildren();state.queue.forEach(p=>{const row=node('div','queue-row');row.append(node('span','',p),node('span','ok','READY'));q.append(row)});if(!state.queue.length)q.textContent='Noch keine Dateien ausgewählt.';$('fileCount').textContent=state.queue.length+' DATEIEN'}
$('chooseFiles').onclick=()=>task(async()=>enqueue(await api.browse()));$('clearQueue').onclick=()=>enqueue([],{replace:true});
const drop=$('dropzone');for(const event of ['dragenter','dragover'])drop.addEventListener(event,e=>{e.preventDefault();drop.classList.add('drag')});for(const event of ['dragleave','drop'])drop.addEventListener(event,e=>{e.preventDefault();drop.classList.remove('drag')});drop.addEventListener('drop',e=>enqueue(api.pathsFromFiles(e.dataTransfer.files)));
$('doImport').onclick=()=>task(async()=>{if(!state.queue.length)return notice('Bitte Dateien auswählen.');$('doImport').disabled=true;try{const res=await api.import({paths:state.queue});$('importOutput').textContent=JSON.stringify(res,null,2);enqueue([],{replace:true});notice(`Katalogisierung: ${res.inserted} neu, ${res.skipped} bereits vorhanden. Warnungen: ${res.warnings.length}`);await refresh()}finally{$('doImport').disabled=false}});
async function loadRows(){const r=await task(()=>api.list({project:$('filterProject').value,category:$('filterCategory').value,search:$('search').value,page:state.page}));if(!r)return;state.rows=r;const list=$('results');list.replaceChildren();r.forEach(x=>{const wrap=node('div','catalog-result');const check=node('input','catalog-check');check.type='checkbox';check.checked=state.multi.has(x.id);check.title='Für Mehrfachaktion auswählen';check.onchange=()=>{check.checked?state.multi.add(x.id):state.multi.delete(x.id);refreshBulkCount()};const b=node('button','result'+(state.selected===x.id?' selected':''));const hd=node('strong','',x.title);const info=node('small','',x.project+' · '+(categories[x.category]||x.category)+' · '+x.source_name);b.append(hd,info,node('span','excerpt',x.excerpt));b.onclick=()=>openRecord(x.id);wrap.append(check,b);list.append(wrap)});refreshBulkCount();if(!r.length)list.textContent='Keine Ergebnisse.';$('pageNumber').textContent=state.page+1}
async function openRecord(id){const r=await task(()=>api.record({id}));if(!r)return;state.selected=id;state.record=r;$('recordInfo').textContent=`${r.title}  |  ${r.project}  |  ${r.category}  |  Quelle: ${r.source_name}  |  Confidence: ${r.confidence}`;$('recordText').textContent=r.content;$('copyContent').disabled=false;$('editTitle').value=r.title;$('editProject').value=r.project;$('editCategory').value=r.category;$('saveMetadata').disabled=false;await loadRows()}
$('saveMetadata').onclick=()=>task(async()=>{if(!state.record)return;const update={id:state.record.id,title:$('editTitle').value,project:$('editProject').value,category:$('editCategory').value};const saved=await api.correct(update);state.record={...state.record,...saved};notice('Katalogeintrag gespeichert. Der Originaltext bleibt unverändert.');await refresh();await loadRows()});
function refreshBulkCount(){$('bulkCount').textContent=state.multi.size+' ausgewählt'}
$('bulkSelectPage').onclick=()=>{state.rows.forEach(r=>state.multi.add(r.id));loadRows()};
$('bulkClear').onclick=()=>{state.multi.clear();loadRows()};
$('bulkApply').onclick=()=>task(async()=>{
 const ids=[...state.multi], project=$('bulkProject').value.trim()||null,category=$('bulkCategory').value||null;
 if(!ids.length)return notice('Bitte Datensätze auswählen.');
 if(!project&&!category)return notice('Zielprojekt oder Kategorie angeben.');
 const out=await api.correct_batch({ids,project,category});state.multi.clear();notice(out.changed+' Datensätze neu zugeordnet; Originaltexte erhalten.');await refresh();await loadRows();
});
$('bulkExport').onclick=()=>task(async()=>{if(!state.multi.size)return notice('Bitte Datensätze auswählen.');const out=await api.export({ids:[...state.multi],format:'zip'});notice('ZIP gespeichert: '+out.path)});
$('bulkArchive').onclick=()=>task(async()=>{const ids=[...state.multi];if(!ids.length)return notice('Bitte Datensätze auswählen.');if(!window.confirm(ids.length+' Datensätze in das alte ZIP-Archiv verschieben?'))return;const out=await api.archive({ids});state.multi.clear();notice('Archiviert: '+out.archived+' Einträge · '+out.path);await refresh();await loadRows()});
$('copyContent').onclick=async()=>{if(!state.record)return;try{await navigator.clipboard.writeText(state.record.content);notice('Vollständiger Datensatztext in Zwischenablage kopiert.')}catch(e){error(e)}};
$('searchBtn').onclick=()=>{state.page=0;loadRows()};$('search').onkeydown=e=>{if(e.key==='Enter'){$('searchBtn').click()}};$('filterProject').onchange=$('filterCategory').onchange=()=>{state.page=0;loadRows()};$('prevPage').onclick=()=>{state.page=Math.max(state.page-1,0);loadRows()};$('nextPage').onclick=()=>{if(state.rows.length===100){state.page++;loadRows()}};
async function doExport(format){const data=state.selected?{ids:[state.selected],format}:{project:$('filterProject').value,format};const r=await task(()=>api.export(data));if(r)notice('Export gespeichert: '+r.path+' ('+r.count+' Datensätze)')}
$('exportJson').onclick=()=>doExport('json');$('exportMarkdown').onclick=()=>doExport('md');$('exportZip').onclick=()=>doExport('zip');
$('archiveSelected').onclick=()=>task(async()=>{if(!state.selected)return notice('Zuerst einen Datensatz öffnen.');const r=await api.archive({ids:[state.selected]});notice('Ins alte Archiv geschrieben: '+r.path);state.selected=null;state.record=null;await refresh();await loadRows()});
async function loadProjects(){const r=await task(()=>api.projects());if(!r)return;const box=$('projectCards');box.replaceChildren();r.forEach(p=>{const el=node('div','project-card');el.append(node('strong','',p.project),node('p','',p.records+' katalogisierte Einträge'),node('p','',`Themen: ${p.topics.map(t=>t[0]+' ('+t[1]+')').join(', ')||'noch keine'}`),node('p','',`Empfehlung: ${p.recommendation}`));box.append(el)});if(!r.length)box.textContent='Noch keine Projekte.'}
async function loadArchived(){const r=await task(()=>api.list({archived:true}));if(!r)return;const el=$('archiveList');el.replaceChildren();r.forEach(x=>el.append(node('div','queue-row',x.project+' · '+x.title)));if(!r.length)el.textContent='Noch keine archivierten Datensätze.'}
$('showArchived').onclick=loadArchived;$('openDataFolder').onclick=()=>task(()=>api.openFolder());
async function checkTools(){const x=await task(()=>api.check());if(!x)return;$('systemInfo').textContent=`Python: ${x.python?.version||'NICHT INSTALLIERT'}\nNode.js: ${x.node}\nElectron: ${x.electron}\nPlattform: ${x.platform}\nSpeicher: ${x.storage}\npypdf: ${x.dependencies?.pypdf?'OK':'FEHLT (optional)'}\npython-docx: ${x.dependencies?.docx?'OK':'FEHLT (optional)'}`}
$('checkTools').onclick=checkTools;$('installExtras').onclick=()=>task(async()=>{const x=await api.install();notice(JSON.stringify(x));await checkTools()});
async function migrate(){const path='../legacy_r02/app/lyrics_library.db';// absolute path resolved in main only, never from renderer
 const r=await task(()=>api.migrate({bundled:true}));if(r){notice(`R02-Migration: ${r.inserted} neu, ${r.duplicates} bereits vorhanden.`);await refresh()}}
$('migrateQuick').onclick=migrate;$('migrateLegacy').onclick=migrate;$('refresh').onclick=refresh;
refresh();

/* R07 additive intelligence UI: DOM textContent, no raw HTML or data mutation. */

function metricCard(label,value){const box=node('div','intel-metric');box.append(node('small','',label),node('strong','',value));return box}
function renderAnalysis(item){
 const out=$('analysisResult');out.replaceChildren();
 const m=item.metrics;
 out.append(node('h3','',item.title),node('p','muted',item.project+' · '+item.category+' · '+(item.source_name||'Unbekannte Quelle')));
 const cards=node('div','intel-metrics');
 [['Wörter',m.word_count],['Textzeilen',m.line_count],['Abschnitte',m.section_count],['Wortvielfalt',m.unique_words],['Ø Wörter/Zeile',m.avg_words_per_line]].forEach(([k,v])=>cards.append(metricCard(k,v)));
 out.append(cards);
 const section=node('div','intel-box');section.append(node('h3','','Abschnittsstruktur'));
 m.sections.forEach(x=>section.append(node('span','intel-chip',x.name+' · Zeile '+x.line)));
 if(!m.sections.length)section.append(node('p','muted','Keine ausdrücklich markierten Lyrics-Abschnitte erkannt.'));
 out.append(section);
 const repetitions=node('div','intel-box');repetitions.append(node('h3','','Wiederholte Textzeilen'));
 m.repeat_lines.forEach(x=>repetitions.append(node('div','intel-row',x.count+' ×  '+x.line)));
 if(!m.repeat_lines.length)repetitions.append(node('p','muted','Keine wiederholten ganzen Textzeilen erkannt.'));
 out.append(repetitions);
 const terms=node('div','intel-box');terms.append(node('h3','','Häufige Begriffe'));const max=Math.max(1,...m.top_terms.map(x=>x.count));
 m.top_terms.forEach(x=>{const wrap=node('div','intel-term');wrap.append(node('span','',x.term));const track=node('div','intel-track'),fill=node('div','intel-fill');fill.style.width=(x.count/max*100)+'%';track.append(fill);wrap.append(track,node('b','',x.count));terms.append(wrap)});
 if(!m.top_terms.length)terms.append(node('p','muted','Keine auswertbaren Begriffe.'));
 out.append(terms,node('p','muted',m.caveat));
}
$('analysisCurrent').onclick=()=>task(async()=>{if(!state.selected)return notice('Bitte erst im Browser einen Datensatz öffnen.');const item=await api.analyze({id:state.selected});renderAnalysis(item)});
$('analysisCompare').onclick=()=>task(async()=>{const ids=[...state.multi];if(ids.length!==2)return notice('Für den Vergleich genau 2 Datensätze markieren.');const r=await api.compare({ids});const out=$('analysisResult');out.replaceChildren();out.append(node('h3','','Zwei Datensätze · Textvergleich'));const cards=node('div','intel-metrics');r.items.forEach(x=>cards.append(metricCard(x.title,x.metrics.word_count+' Wörter · '+x.metrics.line_count+' Zeilen')));out.append(cards,node('p','muted','Gemeinsame häufige Begriffe: '+(r.shared_top_terms.join(', ')||'keine')),node('p','muted',r.comparison_type))});
$('analysisBrowse').onclick=()=>tab('browser');
async function loadProjectInsights(){
 const rows=await task(()=>api.project_insights());if(!rows)return;
 const box=$('projectCards');box.replaceChildren();const largest=Math.max(1,...rows.map(x=>x.active));
 rows.forEach(x=>{const card=node('article','project-card enhanced-project');card.append(node('strong','',x.project));
 const grid=node('div','intel-metrics');grid.append(metricCard('Aktiv',x.active),metricCard('Archiviert',x.archived),metricCard('Quellen (je Kategorie summiert)',x.sources));card.append(grid);
 const bar=node('div','bar'),fill=node('div','bar-inner');fill.style.width=(x.active/largest*100)+'%';bar.append(fill);card.append(bar);
 const cats=node('div','intel-box');cats.append(node('small','muted','Kategorien'));Object.entries(x.categories).sort((a,b)=>b[1]-a[1]).forEach(([label,n])=>cats.append(node('span','intel-chip',(categories[label]||label)+' '+n)));card.append(cats);
 const btn=node('button','btn outline','Im Datenbankbrowser öffnen');btn.onclick=()=>{tab('browser');$('filterProject').value=x.project;state.page=0;loadRows()};card.append(btn);box.append(card)});
 if(!rows.length)box.textContent='Noch keine Projekte.';
}
$('projectRefresh').onclick=loadProjectInsights;
async function loadArchiveR07(){
 const r=await task(()=>api.list({archived:true,search:$('archiveSearch').value,category:$('archiveCategory').value,page:state.archivePage}));
 if(!r)return;
 const el=$('archiveList');el.replaceChildren();
 if(!r.length&&state.archivePage>0){state.archivePage--;return loadArchiveR07()}
 r.forEach(x=>{const b=node('button','result archive-result');b.append(node('strong','',x.title),node('small','',x.project+' · '+(categories[x.category]||x.category)+' · '+x.source_name));b.onclick=async()=>{tab('browser');await openRecord(x.id)};el.append(b)});
 if(!r.length)el.textContent='Keine archivierten Datensätze für diesen Filter.';
 $('archivePage').textContent=String(state.archivePage+1);$('archivePrevious').disabled=state.archivePage===0;$('archiveNext').disabled=r.length<100;
}
$('archiveSearch').onkeydown=e=>{if(e.key==='Enter'){state.archivePage=0;loadArchiveR07()}};
$('archiveCategory').onchange=()=>{state.archivePage=0;loadArchiveR07()};
$('archivePrevious').onclick=()=>{state.archivePage=Math.max(0,state.archivePage-1);loadArchiveR07()};
$('archiveNext').onclick=()=>{state.archivePage++;loadArchiveR07()};
$('showArchived').onclick=()=>{state.archivePage=0;loadArchiveR07()};
