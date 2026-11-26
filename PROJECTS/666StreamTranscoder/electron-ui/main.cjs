'use strict';
// Electron presentation prototype ONLY. No audio/backend process is started.
const { app, BrowserWindow, ipcMain } = require('electron');
const fs = require('fs');
const path = require('path');
const {validateStatus} = require('./status-contract.cjs');
let primaryWindow = null;
function readOnlyStatus(event) {
  if (!primaryWindow || event.sender !== primaryWindow.webContents ||
      event.senderFrame !== primaryWindow.webContents.mainFrame) {
    throw new Error('Unauthorisierter Statusabruf');
  }
  // Fixed path in the original 3DX APP_ID user settings directory. No renderer path input.
  const file = path.join(app.getPath('appData'), '3DXRadioStreamer', 'desktop-status-v1.json');
  try {
    const stat = fs.statSync(file);
    if (!stat.isFile() || stat.size > 4096) return null;
    return validateStatus(JSON.parse(fs.readFileSync(file, 'utf8')), Date.now());
  } catch (_) {
    return null; // fail closed: missing, malformed or outdated snapshot
  }
}
ipcMain.handle('stream:status', readOnlyStatus);
function createWindow() {
  const win = new BrowserWindow({
    width: 1480, height: 940, minWidth: 980, minHeight: 680,
    backgroundColor: '#0b0d19', title: '666StreamTranscoder v3.0 · UI Preview',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true, sandbox: true, nodeIntegration: false,
      webSecurity: true
    }
  });
  primaryWindow = win;
  win.removeMenu();
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', (event, target) => {
    if (target !== win.webContents.getURL()) event.preventDefault();
  });
  win.loadFile(path.join(__dirname, 'index.html'));
}
app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => {
    if (!BrowserWindow.getAllWindows().length) createWindow();
  });
});
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
