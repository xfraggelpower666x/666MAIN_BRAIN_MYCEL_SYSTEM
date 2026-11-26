const {contextBridge,ipcRenderer}=require('electron');
const call=(name,...args)=>ipcRenderer.invoke('cc:'+name,...args);
contextBridge.exposeInMainWorld('cc',Object.freeze({settingsRead:()=>call('settings-read'),settingsSave:s=>call('settings-save',s),choose:()=>call('choose'),folder:()=>call('folder'),start:r=>call('start',r),stop:()=>call('stop'),onEvent:f=>ipcRenderer.on('cc:event',(_,x)=>f(x)),onBoot:f=>ipcRenderer.on('cc:boot',(_,x)=>f(x))}));
