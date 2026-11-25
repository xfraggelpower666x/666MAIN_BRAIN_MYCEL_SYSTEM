'use strict';
const { app, BrowserWindow, dialog, shell, ipcMain } = require('electron');
const { spawn } = require('node:child_process');
const { existsSync, readFileSync } = require('node:fs');
const path = require('node:path');
const {createStore} = require('./settings-store.cjs');
let win, backend, settingsWindow, settingsStore, settings;
const root = path.resolve(__dirname, '..');
const config = JSON.parse(readFileSync(path.join(__dirname, 'config.json'), 'utf8'));
const url = new URL(config.backend_ui_url);
const health = new URL(config.backend_health_url);
function safeLocal(urlObj) {
  if (urlObj.protocol !== 'http:' || urlObj.hostname !== '127.0.0.1') throw new Error('Only loopback HTTP allowed');
}
safeLocal(url);safeLocal(health);
function startBackend() {
  if(app.isPackaged) {
    const exe=path.join(process.resourcesPath,'backend','backend.exe');
    if(!existsSync(exe)) throw new Error('Missing packaged backend.exe');
    backend=spawn(exe,config.python_args||[], {stdio:'ignore',windowsHide:true});
  } else {
    const python=process.env.UNIVERSAL_PYTHON;
    const entry=process.env.UNIVERSAL_PYTHON_ENTRY;
    const project=process.env.UNIVERSAL_PROJECT_ROOT;
    if(!python||!entry||!project) throw new Error('Launch through STARTEN.bat option 6');
    const resolved=path.resolve(project,entry);
    if(!resolved.startsWith(path.resolve(project)+path.sep)) throw new Error('Entry escapes project');
    backend=spawn(python,[resolved,...(config.python_args||[])], {cwd:project,stdio:'ignore',windowsHide:true});
  }
  backend.on('error', err=>{dialog.showErrorBox('Backend start failed',String(err));});
}
async function waitForHealth(timeout=25000) {
  const end=Date.now()+timeout;
  while(Date.now()<end) {
    if(backend && backend.exitCode!==null) throw new Error('Backend ended before ready');
    try {const r=await fetch(health,{signal:AbortSignal.timeout(1200)});if(r.ok)return;}catch{}
    await new Promise(r=>setTimeout(r,350));
  }
  throw new Error('Backend health timeout: '+health.href);
}

// App settings are stored in Electron userData, completely separate from Buildkit config.
function openSettings(){
  if(settingsWindow && !settingsWindow.isDestroyed()){settingsWindow.focus();return;}
  settingsWindow=new BrowserWindow({width:690,height:520,minWidth:540,minHeight:440,show:false,
    parent:win,modal:false,backgroundColor:'#0b0c1b',autoHideMenuBar:true,
    webPreferences:{preload:path.join(__dirname,'settings-preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true,webSecurity:true}});
  settingsWindow.removeMenu();
  settingsWindow.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  settingsWindow.webContents.on('will-navigate',event=>event.preventDefault());
  settingsWindow.loadFile(path.join(__dirname,'renderer','settings.html')).catch(error=>dialog.showErrorBox('Settings',String(error)));
  settingsWindow.once('ready-to-show',()=>settingsWindow.show());
  settingsWindow.on('closed',()=>{settingsWindow=null});
}
function settingsSender(event){
  return settingsWindow && !settingsWindow.isDestroyed() &&
    event.sender===settingsWindow.webContents &&
    event.senderFrame===settingsWindow.webContents.mainFrame;
}
ipcMain.handle('app-settings:load',event=>{
  if(!settingsSender(event))throw new Error('Unauthorized settings request');
  return {...settings};
});
ipcMain.handle('app-settings:save',(event,value)=>{
  if(!settingsSender(event))throw new Error('Unauthorized settings request');
  const saved=settingsStore.save(value);
  settings=saved;
  if(win && !win.isDestroyed())win.setFullScreen(saved.fullscreen);
  return {...settings};
});

function createWindow() {
  win=new BrowserWindow({show:false,fullscreen:settings.fullscreen,kiosk:!!config.electron.kiosk,
    backgroundColor:'#09070f',autoHideMenuBar:true,webPreferences:{preload:path.join(__dirname,'preload.js'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  win.loadFile(path.join(__dirname,'renderer','boot.html'));
  win.once('ready-to-show',()=>win.show());
  win.webContents.setWindowOpenHandler(({url})=>{if(url.startsWith('https://')) shell.openExternal(url);return {action:'deny'};});
  win.webContents.on('will-navigate',(event,target)=>{
    if(target!==url.href && !target.startsWith(url.origin+'/'))event.preventDefault();
  });
  win.webContents.on('before-input-event',(event,input)=>{
    if(input.type==='keyDown' && input.key==='F11'){
      const next=!win.isFullScreen();
      win.setFullScreen(next);
      try{settings=settingsStore.save({...settings,fullscreen:next});}catch(error){dialog.showErrorBox('Settings',String(error));}
    }
    if(input.type==='keyDown' && (input.key==='F10' || (input.control && input.key===',')))openSettings();
  });
}
app.whenReady().then(async()=>{
  settingsStore=createStore(app.getPath('userData'));
  settings=settingsStore.load();
  createWindow();
  try {startBackend();await waitForHealth();await win.loadURL(url.href);}
  catch(e) {dialog.showErrorBox('Application start failed',String(e));win.webContents.send('startup-failed',String(e));}
});
app.on('window-all-closed',()=>app.quit());
app.on('before-quit',()=>{if(backend && backend.exitCode===null){backend.kill();backend=null;}});
