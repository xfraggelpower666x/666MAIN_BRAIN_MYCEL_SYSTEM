'use strict';
const {contextBridge,ipcRenderer}=require('electron');
<<<<<<< HEAD
window.addEventListener('click',event=>{
  if(event.isTrusted && event.target?.closest?.('#overlay-root #audio-input-start:not(:disabled)')){
    ipcRenderer.invoke('audio:overlay-microphone').catch(error=>{
      const status=document.getElementById('audio-input-status');
      if(status)status.textContent='Microphone request error · '+String(error?.message||error);
    });
  }
},true);
=======
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
contextBridge.exposeInMainWorld('rwOverlay',{
  ready:()=>ipcRenderer.invoke('workspace:overlay-ready'),
  action:(payload)=>ipcRenderer.invoke('workspace:overlay-action',payload),
  onInit:(fn)=>ipcRenderer.on('workspace:overlay-init',(_e,payload)=>fn(payload)),
  onSync:(fn)=>ipcRenderer.on('workspace:overlay-sync',(_e,payload)=>fn(payload))
});
