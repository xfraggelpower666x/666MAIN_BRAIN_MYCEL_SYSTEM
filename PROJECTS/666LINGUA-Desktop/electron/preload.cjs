'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('linguaWindow', {
  copy: (text) => ipcRenderer.invoke('lingua:copy', text),
  toggleFullscreen: () => ipcRenderer.invoke('lingua:fullscreen'),
  quit: () => ipcRenderer.invoke('lingua:quit')
});
