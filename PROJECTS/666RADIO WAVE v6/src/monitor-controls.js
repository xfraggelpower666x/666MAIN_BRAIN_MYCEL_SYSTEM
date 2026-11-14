'use strict';
(()=>{
  if(new URLSearchParams(location.search).get('output')==='1'||!window.api)return;
  const q=s=>document.querySelector(s);
  const sourceOne=q('#display-one'),sourceTwo=q('#display-two');
  const quickOne=q('#quick-display-one'),quickTwo=q('#quick-display-two');
  const outputButton=q('#quick-output-toggle'),visualButton=q('#quick-visualizer-toggle');
  const text=key=>{const language=window.RWLocalize?.language?.()||'en-US';const dictionary={
    'en-US':{startOutput:'START OUTPUT',stopOutput:'STOP OUTPUT',openVisualizer:'OPEN VISUALIZER',showVisualizer:'SHOW VISUALIZER',hideVisualizer:'HIDE VISUALIZER',autoFit:'AUTO-FIT',monitorReady:'MONITOR OUTPUT READY',outputsStopped:'VISUAL OUTPUTS STOPPED',outputsActive:'VISUAL OUTPUTS ACTIVE'},
    'de-DE':{startOutput:'AUSGABE STARTEN',stopOutput:'AUSGABE STOPPEN',openVisualizer:'VISUALIZER ÖFFNEN',showVisualizer:'VISUALIZER ANZEIGEN',hideVisualizer:'VISUALIZER AUSBLENDEN',autoFit:'AUTOMATISCH ANPASSEN',monitorReady:'MONITOR-AUSGABE BEREIT',outputsStopped:'VISUAL-AUSGABE GESTOPPT',outputsActive:'VISUAL-AUSGABE AKTIV'}
  };return dictionary[language][key]||key;};
  const copyOptions=(from,to)=>{
    if(!from||!to)return;
    const selected=from.value;
    to.replaceChildren(...Array.from(from.options,o=>new Option(o.textContent,o.value,o.defaultSelected,o.selected)));
    if(Array.from(to.options).some(o=>o.value===selected))to.value=selected;
  };
  const syncOptions=()=>{copyOptions(sourceOne,quickOne);copyOptions(sourceTwo,quickTwo);};
  syncOptions();
  for(const select of [sourceOne,sourceTwo]){
    if(!select)continue;
    new MutationObserver(syncOptions).observe(select,{childList:true,subtree:true,attributes:true,attributeFilter:['selected']});
    select.addEventListener('change',syncOptions);
  }
  const mapToLegacy=()=>{
    if(sourceOne&&quickOne)sourceOne.value=quickOne.value;
    if(sourceTwo&&quickTwo)sourceTwo.value=quickTwo.value;
    localStorage.setItem('s666-display-one',quickOne?.value||'');
    localStorage.setItem('s666-display-two',quickTwo?.value||'');
  };
  async function refreshState(){
    try{
      const state=await window.api.outputStatus(),active=Array.isArray(state?.active)?state.active:[];
      const selected=[quickOne?.value,quickTwo?.value].filter(Boolean).map(Number);
      const allSelectedActive=selected.length>0&&selected.every(id=>active.some(output=>Number(output.id)===id));
      if(outputButton)outputButton.textContent=text(allSelectedActive?'stopOutput':'startOutput');
      if(visualButton)visualButton.textContent=state?.detachedVisualizer?text(state.detachedVisualizer.visible?'hideVisualizer':'showVisualizer'):text('openVisualizer');
    }catch(error){if(outputButton)outputButton.title='Monitor status unavailable: '+String(error.message||error);}
  }
  outputButton?.addEventListener('click',async()=>{
    const ids=[quickOne?.value,quickTwo?.value].filter(Boolean).map(Number);
    if(new Set(ids).size!==ids.length){if(quickTwo)quickTwo.value='';}
    mapToLegacy();
    try{
      const state=await window.api.outputStatus(),active=Array.isArray(state?.active)?state.active:[];
      const selection=[quickOne?.value,quickTwo?.value].filter(Boolean).map(Number);
      const stop=selection.length>0&&selection.every(id=>active.some(output=>Number(output.id)===id));
      const result=await window.api.openOutputs(stop?[]:selection);
      q('#quick-monitor-state').textContent=stop?text('outputsStopped'):`${text('outputsActive')} · ${result.displayIds.length}`;
      await refreshState();
    }catch(error){q('#quick-monitor-state').textContent='OUTPUT ERROR · '+String(error.message||error);}
  });
  visualButton?.addEventListener('click',async()=>{
    try{await window.api.toggleDetachedVisualizer();await refreshState();}
    catch(error){q('#quick-monitor-state').textContent='VISUALIZER ERROR · '+String(error.message||error);}
  });
  q('#quick-visualizer-fit')?.addEventListener('click',async()=>{
    try{
      const state=await window.api.outputStatus();
      if(!state?.detachedVisualizer){await window.api.toggleDetachedVisualizer();await new Promise(resolve=>setTimeout(resolve,300));}
      const result=await window.api.autoFitDetachedVisualizer();
      q('#quick-monitor-state').textContent=`VISUALIZER FIT · DISPLAY ${result.displayId}`;
      await refreshState();
    }catch(error){q('#quick-monitor-state').textContent='AUTO-FIT ERROR · '+String(error.message||error);}
  });
  window.api.onDisplaysChanged?.(()=>{syncOptions();refreshState();});
  window.addEventListener('rw:language-changed',()=>{
    q('#quick-visualizer-fit').textContent=text('autoFit');
    refreshState();
  });
  q('#quick-monitor-state').textContent=text('monitorReady');
  refreshState();
  setInterval(()=>{if(!document.hidden)refreshState();},5000);
})();
