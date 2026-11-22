const {contextBridge, ipcRenderer, webUtils}=require('electron');
const allowed=['status','import','browse','list','record','correct','export','archive','projects','migrate','check','install','openFolder'];
contextBridge.exposeInMainWorld('catalog',{...Object.fromEntries(allowed.map(k=>[k,(data={})=>ipcRenderer.invoke('catalog:'+k,data)])),pathsFromFiles:(files)=>Array.from(files).map(f=>webUtils.getPathForFile(f)).filter(Boolean)});
