// Settings renderer has no filesystem or Node access.
'use strict';
const els=Object.fromEntries(['fullscreen','language','theme','save','state'].map(id=>[id,document.getElementById(id)]));
async function reload(){try{const s=await window.applicationSettings.load();els.fullscreen.checked=s.fullscreen;els.language.value=s.language;els.theme.value=s.theme;els.state.textContent='Einstellungen geladen.';}catch(error){els.state.textContent='Ladefehler: '+error.message;}}
els.save.addEventListener('click',async()=>{
  els.save.disabled=true;
  try{await window.applicationSettings.save({fullscreen:els.fullscreen.checked,language:els.language.value,theme:els.theme.value});els.state.textContent='Einstellungen gespeichert.';}
  catch(error){els.state.textContent='Speichern fehlgeschlagen: '+error.message;}
  finally{els.save.disabled=false;}
});
reload();
