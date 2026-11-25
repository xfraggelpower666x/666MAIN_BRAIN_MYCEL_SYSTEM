// Only used by the local settings window, never by remote backend UI.
'use strict';
const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('applicationSettings',Object.freeze({
  load:()=>ipcRenderer.invoke('app-settings:load'),
  save:(settings)=>ipcRenderer.invoke('app-settings:save',settings)
}));
