'use strict'

const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('engineBridge', {
  onRun(callback) {
    ipcRenderer.on('engine:run', (_event, task) => callback(task))
  },
  output(stream, text) {
    ipcRenderer.send('engine:output', { stream, text })
  },
  result(files) {
    ipcRenderer.send('engine:result', files)
  },
  error(message) {
    ipcRenderer.send('engine:error', message)
  }
})
