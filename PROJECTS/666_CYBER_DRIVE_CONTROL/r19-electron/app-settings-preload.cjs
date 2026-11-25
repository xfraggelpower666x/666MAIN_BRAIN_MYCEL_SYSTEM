'use strict';
const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('applicationSettings',Object.freeze({
  load:()=>ipcRenderer.invoke('app-settings:load'),
  save:s=>ipcRenderer.invoke('app-settings:save',s)
}));
