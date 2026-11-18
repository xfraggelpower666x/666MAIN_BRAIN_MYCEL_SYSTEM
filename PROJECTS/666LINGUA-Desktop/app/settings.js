'use strict';

let desktop={language:'en',person:null,partner:null,targetZone:'',from:'en',to:'de',revision:0};
let cities;
let currentConversion=null;
const displayZones=new Intl.DisplayNames(['en'],{type:'region'});
const places=[];
const deviceZone=Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
const knownZones=new Set(['UTC',deviceZone,...(Intl.supportedValuesOf?.('timeZone') ?? [])]);
const zoneList=el('zones');
const timezoneFields=['person-zone','partner-zone','target-zone'];
const zodiacNames={
  capricorn:'Steinbock',aquarius:'Wassermann',pisces:'Fische',aries:'Widder',taurus:'Stier',gemini:'Zwillinge',
  cancer:'Krebs',leo:'Löwe',virgo:'Jungfrau',libra:'Waage',scorpio:'Skorpion',sagittarius:'Schütze'
};
const zodiacSymbols=Array.from('♑♒♓♈♉♊♋♌♍♎♏♐');
const emojiCache=new Map();
const dateFormats=new Map();
let emojiData;
let emojiSelection;

function validZone(value) {
  if(!/^[A-Za-z]/.test(value) || value==='Local')return false;
  try { new Intl.DateTimeFormat('en',{timeZone:value}); return true; }
  catch { return false; }
}

function fillZones() {
  zoneList.replaceChildren(...Array.from(knownZones).sort().map(value=>{const option=node('option');option.value=value;return option;}));
}
fillZones();
for(const id of timezoneFields)el(id).addEventListener('input',()=>el(id).setCustomValidity(''));

function formatter(language,timeZone,kind) {
  const key=[language,timeZone,kind].join('/');
  if(!dateFormats.has(key)) {
    const formats={
      clock:{hour:'2-digit',minute:'2-digit',second:'2-digit'},
      date:{weekday:'long',year:'numeric',month:'long',day:'numeric'},
      offset:{timeZoneName:'shortOffset'},
      numeric:{year:'numeric',month:'numeric',day:'numeric',calendar:'iso8601',numberingSystem:'latn'}
    };
    dateFormats.set(key,new Intl.DateTimeFormat(language,{timeZone,...formats[kind]}));
  }
  return dateFormats.get(key);
}

function calendarDay(now,timeZone) {
  const parts=Object.fromEntries(formatter('en-GB',timeZone,'numeric').formatToParts(now).map(x=>[x.type,x.value]));
  // ISO-Hilfsdatum, damit auch Monats- und Jahresgrenzen erkannt werden.
  const day=new Date(0);
  day.setUTCFullYear(Number(parts.year),Number(parts.month)-1,Number(parts.day));
  return day.getTime()/86400000;
}

function offset(now,timeZone) {
  return formatter('en',timeZone,'offset').formatToParts(now).find(x=>x.type==='timeZoneName')?.value || 'GMT';
}

function shiftText(shift) {
  if(shift===0)return t('Gleiches Kalenderdatum');
  if(shift===-1)return t('Vorheriger Kalendertag');
  if(shift===1)return t('Nächster Kalendertag');
  return (shift>0?'+':'')+shift+' d';
}

function refreshClocks() {
  const now=new Date();
  const home=desktop.person?.zone || deviceZone;
  const target=desktop.targetZone;
  const to=el('to').value;
  const language=targetLocales[to] ?? locale();
  el('home-clock-label').textContent=desktop.person?.name || t('Deine Ortszeit');
  el('home-time').textContent=formatter(locale(),home,'clock').format(now);
  el('home-date').textContent=formatter(locale(),home,'date').format(now);
  el('home-time').dateTime=now.toISOString();
  el('home-zone').textContent=[desktop.person?.city || t('Gerätezeitzone'),home,offset(now,home)].join(' · ');
  el('target-language').textContent=names[to] ?? t('Zielsprache');
  const confirmed=Boolean(target);
  el('target-time').textContent=confirmed?formatter(language,target,'clock').format(now):'—';
  el('target-date').textContent=confirmed?formatter(language,target,'date').format(now):'';
  el('target-time').dateTime=confirmed?now.toISOString():'';
  el('day-shift').textContent=confirmed?offset(now,target)+' · '+shiftText(calendarDay(now,target)-calendarDay(now,home)):t('Zielzeitzone auswählen.');
  el('target-zone').placeholder=t('Zielzeitzone');
  el('time-route').textContent=home+' → '+(target || t('Zielzeitzone auswählen.'));
}

function formatDifference(minutes) {
  const hours=Math.trunc(Math.abs(minutes)/60);
  const rest=Math.abs(minutes)%60;
  return (minutes<0?'−':'+')+hours+' h '+String(rest).padStart(2,'0')+' min';
}

function displayConversion() {
  if(!currentConversion)return;
  const {result,request}=currentConversion;
  const when=new Date(result.instant);
  const language=targetLocales[el('to').value] || locale();
  const fromDate=formatter(locale(),request.fromZone,'date').format(when);
  const fromTime=formatter(locale(),request.fromZone,'clock').format(when);
  const toDate=formatter(language,request.toZone,'date').format(when);
  const toTime=formatter(language,request.toZone,'clock').format(when);
  el('time-result').textContent=fromDate+' · '+fromTime+' (UTC'+result.sourceOffset+') → '+toDate+' · '+toTime+' (UTC'+result.targetOffset+') · '+formatDifference(result.differenceMinutes)+' · '+shiftText(result.dayShift)+' · '+t('Eindeutige Umrechnung mit Sommerzeitregeln');
}
function invalidateConversion(){
  currentConversion=null;
  el('time-result').textContent='';
}

function applyLocale(language) {
  setStaticLanguage(language);
  updateLanguageOptions();
  refreshInput();
  if(currentResult)render(currentResult.result);
  else clearResult();
  updateSystemInfo();
  if(el('memory').open)loadMemory();
  if(el('dictionary').open)renderDictionary();
  refreshClocks();
  displayConversion();
}

function acceptSettings(data) {
  if(data.revision<desktop.revision)return;
  desktop=data;
}

function applyRoute() {
  el('from').value=desktop.from;
  el('to').value=desktop.to;
  clearResult();
  refreshInput();
  refreshClocks();
}

let routeSaving=false;
async function saveRoute(changed) {
  if(routeSaving)return;
  const from=el('from');
  const to=el('to');
  if(from.value===to.value){
    if(changed==='from')to.value=desktop.from;
    else from.value=desktop.to;
  }
  routeSaving=true;
  for(const id of ['from','to','swap'])el(id).disabled=true;
  try{acceptSettings(await api('route',{from:from.value,to:to.value}));}
  catch(error){status(error.message);}
  finally{
    for(const id of ['from','to','swap'])el(id).disabled=false;
    routeSaving=false;
    applyRoute();
    displayConversion();
  }
}

el('ui-language').addEventListener('change',async()=> {
  const select=el('ui-language');
  select.disabled=true;
  try{
    acceptSettings(await api('language',{language:select.value}));
    applyLocale(desktop.language);
  }catch(error){status(error.message);}
  finally{select.value=desktop.language;select.disabled=false;}
});

el('target-zone').addEventListener('change',async(event)=>{
  const field=event.target;
  const value=field.value.trim();
  if(value && !validZone(value)){
    el('target-zone-status').textContent=t('Zeitzone auswählen.');
    field.setAttribute('aria-invalid','true');
    return;
  }
  const previous=desktop.targetZone;
  field.disabled=true;
  try {
    acceptSettings(await api('target-zone',{zone:value}));
    field.value=desktop.targetZone;
    field.removeAttribute('aria-invalid');
    el('target-zone-status').textContent='';
    invalidateConversion();
    refreshClocks();
  } catch(error) {
    field.value=previous;
    el('target-zone-status').textContent=error.message;
  } finally { field.disabled=false; }
});
for(const id of ['from','to','swap'])el(id).addEventListener(id==='swap'?'click':'change',()=>saveRoute(id));

function placeKey(value){return value.normalize('NFD').replace(/\p{M}/gu,'').trim().toLocaleLowerCase('en');}
function placeLabel(row) {
  const country=/^[A-Z]{2}$/.test(row[2])?displayZones.of(row[2]):'';
  return [row[0],row[1],country].filter(Boolean).join(' · ');
}

const placeAliases={
  'munchen':'munich','muenchen':'munich','koln':'cologne','koeln':'cologne',
  'wien':'vienna','zurich':'zurich','rom':'rome','neapel':'naples',
  'milan':'milan','mailand':'milan','prag':'prague','warschau':'warsaw'
};

function updatePlace(type) {
  const city=el(type+'-city');
  const field=el(type+'-zone');
  const hint=el(type+'-hint');
  const dataList=el(type+'-cities');
  const input=placeKey(city.value);
  const query=placeAliases[input] || input;
  dataList.replaceChildren();
  field.value='';
  if(!cities || !query) {hint.textContent='';return;}
  const options=[];
  const exact=[];
  for(const [row,labelKey,name,ascii] of places){
    if(labelKey===input){
      exact.length=0;exact.push(row);break;
    }
    if(name===query||ascii===query)exact.push(row);
    if(options.length<24&&(name.startsWith(query)||ascii.startsWith(query)))options.push(row);
  }
  const proposals=exact.length>1?exact.slice(0,40):options;
  const labels=[...new Set(proposals.map(placeLabel))];
  dataList.replaceChildren(...labels.map(value=>{const option=node('option');option.value=value;return option;}));
  const choices=[...new Set(exact.map(row=>row[3]))];
  if(choices.length===1 && validZone(choices[0])){
    field.value=choices[0];
    field.setCustomValidity('');
    hint.textContent=t('Ort erkannt')+' · '+choices[0];
  }else{
    hint.textContent=t(choices.length>1?'Mehrere Orte gefunden. Wähle Ort und Region.':'Kein eindeutiger Ort im Offline-Verzeichnis. Wähle die Zeitzone.');
  }
}

async function loadCities() {
  if(cities)return;
  try {
    const response=await fetch('cities.json');
    if(!response.ok)throw new Error();
    const rows=await response.json();
    const entries=[];
    for(const row of rows){
      knownZones.add(row[3]);
      entries.push([row,placeKey(placeLabel(row)),placeKey(row[0]),placeKey(row[4])]);
    }
    places.splice(0,places.length,...entries);
    cities=rows;
    for(const type of ['person','partner']){
      if(el(type+'-city').value && !el(type+'-zone').value)updatePlace(type);
    }
    fillZones();
  } catch {el('profile-status').textContent=t('Ortsverzeichnis konnte nicht geladen werden.');}
}

function updateZodiac() {
  const match=/^\d{4}-(\d\d)-(\d\d)$/.exec(el('person-birth').value);
  let text='—';
  if(match){
    const starts=[20,19,21,20,21,21,23,23,23,23,22,22];
    const month=Number(match[1])-1;
    const index=(month+(Number(match[2])>=starts[month]?1:0))%12;
    text=zodiacSymbols[index]+' '+t(Object.values(zodiacNames)[index]);
  }
  el('person-zodiac').textContent=text;
}

function enablePartner() {
  const enable=el('partner-enabled').checked;
  el('partner-fields').hidden=!enable;
  el('partner-zone').required=enable;
}

function fillProfile() {
  const {person,partner}=desktop;
  for(const key of ['name','city','zone','birth']) {
    el('person-'+key).value=person?.[key] || '';
    el('person-'+key).setCustomValidity('');
  }
  for(const key of ['name','city','zone','language']){
    el('partner-'+key).value=partner?.[key] || (key==='language'?el('to').value:'');
    el('partner-'+key).setCustomValidity('');
  }
  el('partner-enabled').checked=Boolean(partner);
  el('profile-delete').hidden=!person;
  el('profile-status').textContent='';
  for(const type of ['person','partner'])el(type+'-hint').textContent='';
  updateZodiac();
  enablePartner();
}

el('profile-open').addEventListener('click',()=>{
  fillProfile();
  el('profile-dialog').showModal();
  loadCities();
});
el('profile-close').addEventListener('click',()=>el('profile-dialog').close());
el('person-birth').addEventListener('input',updateZodiac);
el('partner-enabled').addEventListener('change',enablePartner);
for(const type of ['person','partner'])el(type+'-city').addEventListener('input',()=>updatePlace(type));

async function saveProfile(person,partner) {
  el('profile-save').disabled=true;
  el('profile-delete').disabled=true;
  try{
    acceptSettings(await api('profile',{person,partner}));
    el('target-zone').value=desktop.targetZone;
    el('target-zone').removeAttribute('aria-invalid');
    el('target-zone-status').textContent='';
    applyRoute();
    invalidateConversion();
    refreshClocks();
    el('profile-dialog').close();
    status(t(person?'Profil lokal gespeichert.':'Lokales Profil gelöscht.'));
  }catch(error){el('profile-status').textContent=error.message;}
  finally{el('profile-save').disabled=false;el('profile-delete').disabled=false;}
}

el('profile-form').addEventListener('submit',event=>{
  event.preventDefault();
  const fields=(type,keys)=>Object.fromEntries(keys.map(key=>[key,el(type+'-'+key).value.trim()]));
  const person=fields('person',['name','city','zone','birth']);
  const partner=el('partner-enabled').checked?fields('partner',['name','city','zone','language']):null;
  const invalid=!validZone(person.zone)?'person-zone':partner&&!validZone(partner.zone)?'partner-zone':'';
  if(invalid){
    el(invalid).setCustomValidity(t('Zeitzone auswählen.'));
    el(invalid).reportValidity();
    return;
  }
  saveProfile(person,partner);
});
el('profile-delete').addEventListener('click',()=>{
  if(confirm(t('Lokales Profil und Gesprächspartner löschen?')))saveProfile(null,null);
});

el('time-form').addEventListener('submit',async(event)=>{
  event.preventDefault();
  invalidateConversion();
  const request={
    date:el('convert-date').value,time:el('convert-time').value,
    fromZone:desktop.person?.zone||deviceZone,toZone:desktop.targetZone
  };
  try{
    const result=await api('temporal',request);
    currentConversion={result,request};
    displayConversion();
  }catch(error){el('time-result').textContent=error.message;}
});
for(const id of ['convert-date','convert-time'])el(id).addEventListener('input',invalidateConversion);

const temporalWords=/\b(?:today|tomorrow|yesterday|tonight|this (?:morning|afternoon|evening)|next (?:morning|day|week)|monday|tuesday|wednesday|thursday|friday|saturday|sunday|heute|morgen|gestern|übermorgen|montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag|hoy|mañana|ayer|ontem|amanhã)\b|\b\d{1,2}:\d{2}\b|\b\d{4}-\d{2}-\d{2}\b/iu;
function temporalHint() {
  el('temporal-hint').textContent=temporalWords.test(source.value)?t('Zeitangabe im Text erkannt. Für eine Umrechnung nutze Datum, Uhrzeit und beide Zeitzonen.'):'';
}
source.addEventListener('input',temporalHint);
el('previous').addEventListener('click',temporalHint);
el('ui-language').addEventListener('change',()=>setTimeout(temporalHint,250));

function renderEmojiGrid() {
  if(!emojiData)return;
  const grid=el('emoji-grid');
  const text=placeKey(el('emoji-search').value);
  const category=el('emoji-category').value;
  const hits=emojiData.data.filter(([emoji,label,group,tags])=>(category===''||Number(category)===group)&&
    (!text||emoji.includes(text)||placeKey(label+' '+tags).includes(text)));
  const fragment=document.createDocumentFragment();
  for(const [emoji,label] of hits){
    const button=node('button',emoji);
    button.type='button';
    button.title=label;
    button.setAttribute('aria-label',label+' '+emoji);
    button.dataset.emoji=emoji;
    fragment.append(button);
  }
  grid.replaceChildren(fragment);
  grid.scrollTop=0;
  el('emoji-status').textContent=hits.length?hits.length.toLocaleString(locale()):t('Keine passenden Emojis.');
}
let emojiRenderTimer;
el('emoji-search').addEventListener('input',()=>{
  clearTimeout(emojiRenderTimer);
  emojiRenderTimer=setTimeout(renderEmojiGrid,70);
});
el('emoji-category').addEventListener('change',renderEmojiGrid);

el('emoji-open').addEventListener('click',async()=>{
  emojiSelection=[source.selectionStart,source.selectionEnd];
  const dialog=el('emoji-dialog');
  el('emoji-search').value='';
  el('emoji-grid').replaceChildren();
  el('emoji-status').textContent='…';
  dialog.showModal();
  el('emoji-search').focus();
  try{
    if(!emojiCache.has(uiLanguage)){
      const response=await fetch('emoji-'+uiLanguage+'.json');
      if(!response.ok)throw new Error();
      emojiCache.set(uiLanguage,await response.json());
    }
    emojiData=emojiCache.get(uiLanguage);
    const category=el('emoji-category');
    category.replaceChildren(node('option',t('Alle Emojis')));
    category.options[0].value='';
    for(const [idx,label] of emojiData.groups.entries()){
      const option=node('option',label);
      option.value=idx;
      category.append(option);
    }
    renderEmojiGrid();
  }catch {el('emoji-status').textContent=t('Emojis konnten nicht geladen werden.');}
});
el('emoji-grid').addEventListener('click',event=>{
  const button=event.target.closest('button[data-emoji]');
  if(!button)return;
  const emoji=button.dataset.emoji;
  const [start,end]=emojiSelection;
  if(Array.from(source.value.slice(0,start)+emoji+source.value.slice(end)).length>12000){
    el('emoji-status').textContent=t('Die Eingabe hat bereits 12.000 Zeichen.');
    return;
  }
  source.setRangeText(emoji,start,end,'end');
  source.dispatchEvent(new Event('input'));
  el('emoji-dialog').close();
  source.focus();
  source.setSelectionRange(start+emoji.length,start+emoji.length);
  status(t('Emoji eingefügt.'));
});
el('emoji-close').addEventListener('click',()=>el('emoji-dialog').close());

el('fullscreen').addEventListener('click',async()=>{
  if(document.fullscreenElement)return;
  try{await document.documentElement.requestFullscreen();}
  catch{status(t('Vollbild konnte nicht aktiviert werden.'));}
});
const liveTimer=setInterval(refreshClocks,1000);
el('quit').addEventListener('click',()=>clearInterval(liveTimer));
refreshClocks();
const startupSettings = api('settings').then(saved=>{
  acceptSettings(saved);
  el('ui-language').value=desktop.language;
  el('target-zone').value=desktop.targetZone;
  applyLocale(desktop.language);
  applyRoute();
  refreshClocks();
  return true;
}).catch(error=>{status(error.message);return false;});

el('notice-panel').addEventListener('toggle',async(event)=>{
  if(!event.target.open || el('notice-copy').dataset.loaded)return;
  try{
    const response=await fetch('notices.txt');
    if(!response.ok)throw new Error();
    el('notice-copy').textContent=await response.text();
    el('notice-copy').dataset.loaded='true';
  }catch{el('notice-copy').textContent=t('Hinweise konnten nicht geladen werden.');}
});
