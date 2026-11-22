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
  setDriveVisibility:(id,target,enabled)=>ipcRenderer.invoke('set-drive-visibility',id,target,enabled),
  setOverlayLayout:layout=>ipcRenderer.invoke('set-overlay-layout',layout),
  showMain:()=>ipcRenderer.invoke('show-main')
});
