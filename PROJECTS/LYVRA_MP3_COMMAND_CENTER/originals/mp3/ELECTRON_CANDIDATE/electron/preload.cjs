const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('lyvra',Object.freeze({
  choose:kind=>ipcRenderer.invoke('lyvra:choose',kind),
  scan:dir=>ipcRenderer.invoke('lyvra:scan',dir),
  start:request=>ipcRenderer.invoke('lyvra:start',request),
  stop:()=>ipcRenderer.invoke('lyvra:stop'),
  check:()=>ipcRenderer.invoke('lyvra:check'),
  monitor:()=>ipcRenderer.invoke('lyvra:monitor'),
  onStatus:fn=>{const cb=(_e,data)=>fn(data);ipcRenderer.on('lyvra:status',cb);return ()=>ipcRenderer.removeListener('lyvra:status',cb)}
}));
