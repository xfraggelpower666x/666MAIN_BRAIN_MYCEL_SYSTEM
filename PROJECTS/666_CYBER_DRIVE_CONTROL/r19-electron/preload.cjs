'use strict';
const {contextBridge, ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('cyber',{
  readMetrics:()=>ipcRenderer.invoke('get-latest'),
  onMetrics:(handler)=>{
    if(typeof handler!=='function')return()=>{};
    const fn=(_evt,data)=>handler(data);
    ipcRenderer.on('metrics',fn);
    return()=>ipcRenderer.removeListener('metrics',fn);
  },
  toggleOverlay:()=>ipcRenderer.invoke('overlay-toggle'),
  showMain:()=>ipcRenderer.invoke('show-main')
});
