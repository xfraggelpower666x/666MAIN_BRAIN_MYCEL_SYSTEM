const {contextBridge,ipcRenderer,webUtils}=require('electron');
contextBridge.exposeInMainWorld('autodj',Object.freeze({
 chooseFiles:()=>ipcRenderer.invoke('files:choose'),
 validateFiles:files=>ipcRenderer.invoke('files:validate',files),
 pathsFromFiles:files=>Array.from(files).map(f=>webUtils.getPathForFile(f)),
 chooseFolder:()=>ipcRenderer.invoke('folder:choose'),
 inspectCoverFolder:folder=>ipcRenderer.invoke('covers:inspect',folder),
 start:opts=>ipcRenderer.invoke('job:start',opts),
 cancel:()=>ipcRenderer.invoke('job:abort'),
 onEvent:listener=>{const h=(_,data)=>listener(data);ipcRenderer.on('job:event',h);return()=>ipcRenderer.removeListener('job:event',h);}
}));
