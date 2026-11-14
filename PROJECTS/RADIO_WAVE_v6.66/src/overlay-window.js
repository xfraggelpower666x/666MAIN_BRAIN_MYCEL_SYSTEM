'use strict';
(()=>{
  const root=document.getElementById('overlay-root');
  let overlayKey='';
  const applyControls=(controls=[])=>{
    for(const s of controls){
      if(!s?.id)continue;
      const el=document.getElementById(s.id);
      if(!el)continue;
      if((el.type==='checkbox'||el.type==='radio')&&typeof s.checked==='boolean')el.checked=s.checked;
      else if(s.value!==undefined&&s.value!==null)el.value=String(s.value);
      if(typeof s.disabled==='boolean')el.disabled=s.disabled;
    }
  };
  const wire=()=>{
    root.addEventListener('input',e=>{
      const el=e.target;
      if(!el?.id||!el.matches('input,select,textarea'))return;
      window.rwOverlay.action({key:overlayKey,kind:'input',id:el.id,value:el.value,checked:!!el.checked}).catch(()=>{});
    },true);
    root.addEventListener('change',e=>{
      const el=e.target;
      if(!el?.id||!el.matches('input,select,textarea'))return;
      window.rwOverlay.action({key:overlayKey,kind:'change',id:el.id,value:el.value,checked:!!el.checked}).catch(()=>{});
    },true);
    root.addEventListener('click',e=>{
      const b=e.target.closest('button');
      if(!b)return;
      const action=b.id?{id:b.id}:{selector:b.dataset.source?('[data-source="'+CSS.escape(b.dataset.source)+'"]'):(b.dataset.openWindow?('[data-open-window="'+CSS.escape(b.dataset.openWindow)+'"]'):'')};
      if(!action.id&&!action.selector)return;
      window.rwOverlay.action({key:overlayKey,kind:'click',...action}).catch(()=>{});
    },true);
  };
  const sanitizeHtml=html=>{
    const doc=new DOMParser().parseFromString(String(html||''),'text/html');
    doc.querySelectorAll('script,style,iframe,frame,object,embed,link,meta,base,form,svg,math,template').forEach(n=>n.remove());
    doc.body.querySelectorAll('*').forEach(el=>{
      for(const a of Array.from(el.attributes)){
        const n=a.name.toLowerCase(),v=a.value.replace(/[\u0000-\u0020]/g,'').toLowerCase();
        if(n.startsWith('on')||n==='srcdoc'||n==='formaction'||((n==='href'||n==='src'||n==='xlink:href')&&!/^(https:|data:image\/(png|jpe?g|gif|webp);|#)/.test(v)))el.removeAttribute(a.name);
      }
    });
    return doc.body.innerHTML;
  };
  window.rwOverlay.onInit(payload=>{
    overlayKey=String(payload?.key||'');
    document.title='RADIO WAVE · '+String(payload?.title||overlayKey||'CONTROL');
    root.innerHTML=sanitizeHtml(payload?.html);
    applyControls(payload?.controls||[]);
    wire();
  });
  window.rwOverlay.onSync(payload=>{
    if(payload?.html!==undefined)root.innerHTML=sanitizeHtml(payload.html);
    applyControls(payload?.controls||[]);
  });
  window.rwOverlay.ready().catch(()=>{});
})();
