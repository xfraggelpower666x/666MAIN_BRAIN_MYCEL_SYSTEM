'use strict';
(()=>{
  const root=document.getElementById('rw-about');
  if(!root||!window.api?.openExternalLink)return;
  root.addEventListener('click',async event=>{
    const button=event.target.closest('[data-external-url],a.rw-about-email');
    if(!button)return;
    event.preventDefault();
    const state=document.getElementById('rw-about-state');
    if(state)state.textContent='OPENING · '+button.textContent.trim();
    try{
      await window.api.openExternalLink(button.dataset.externalUrl||button.href);
      if(state)state.textContent='OPENED · '+button.textContent.trim();
    }catch(error){
      if(state)state.textContent='LINK ERROR · '+String(error.message||error);
    }
  });
})();
