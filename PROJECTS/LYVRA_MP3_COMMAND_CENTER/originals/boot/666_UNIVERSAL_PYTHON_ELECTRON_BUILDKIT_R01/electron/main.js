'use strict';
const { app, BrowserWindow, dialog, shell } = require('electron');
const { spawn } = require('node:child_process');
const { existsSync, readFileSync } = require('node:fs');
const path = require('node:path');
let win, backend;
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
function createWindow() {
  win=new BrowserWindow({show:false,fullscreen:!!config.electron.fullscreen,kiosk:!!config.electron.kiosk,
    backgroundColor:'#09070f',autoHideMenuBar:true,webPreferences:{preload:path.join(__dirname,'preload.js'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  win.loadFile(path.join(__dirname,'renderer','boot.html'));
  win.once('ready-to-show',()=>win.show());
  win.webContents.setWindowOpenHandler(({url})=>{if(url.startsWith('https://')) shell.openExternal(url);return {action:'deny'};});
  win.webContents.on('will-navigate',(event,target)=>{
    if(target!==url.href && !target.startsWith(url.origin+'/'))event.preventDefault();
  });
  win.webContents.on('before-input-event',(event,input)=>{
    if(input.type==='keyDown' && input.key==='F11')win.setFullScreen(!win.isFullScreen());
  });
}
app.whenReady().then(async()=>{
  createWindow();
  try {startBackend();await waitForHealth();await win.loadURL(url.href);}
  catch(e) {dialog.showErrorBox('Application start failed',String(e));win.webContents.send('startup-failed',String(e));}
});
app.on('window-all-closed',()=>app.quit());
app.on('before-quit',()=>{if(backend && backend.exitCode===null){backend.kill();backend=null;}});
