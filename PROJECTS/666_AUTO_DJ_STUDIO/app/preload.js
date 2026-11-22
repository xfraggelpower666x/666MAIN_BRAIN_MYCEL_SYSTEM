const {contextBridge,ipcRenderer,webUtils}=require('electron');
contextBridge.exposeInMainWorld('autodj',Object.freeze({
 chooseFiles:()=>ipcRenderer.invoke('files:choose'),
 validateFiles:paths=>ipcRenderer.invoke('files:validate',paths),
 pathsFromFiles:files=>Array.from(files).map(f=>webUtils.getPathForFile(f)),
 chooseFolder:()=>ipcRenderer.invoke('folder:choose'),
 start:opts=>ipcRenderer.invoke('job:start',opts),
 cancel:()=>ipcRenderer.invoke('job:cancel'),
 onEvent:fn=>{const cb=(_,x)=>fn(x);ipcRenderer.on('job:event',cb);return ()=>ipcRenderer.removeListener('job:event',cb);}
}));
