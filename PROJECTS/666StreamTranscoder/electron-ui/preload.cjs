'use strict';
// Explicit read-only presentation contract, no IPC/backend permissions yet.
const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('streamUi', Object.freeze({
  mode: 'DISCONNECTED_PREVIEW',
  engineConnected: false,
  canBroadcast: false,
  canMonitor: false,
  canChangeSettings: false,
  getStatus: () => ipcRenderer.invoke('stream:status')
}));
