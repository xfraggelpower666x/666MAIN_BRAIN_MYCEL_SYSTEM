const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('buildkit',Object.freeze({
  action:(id)=>ipcRenderer.invoke('buildkit:action',id),
  quit:()=>ipcRenderer.invoke('buildkit:quit')
}));
