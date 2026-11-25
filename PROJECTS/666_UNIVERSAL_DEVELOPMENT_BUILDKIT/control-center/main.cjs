// 666 Universal Buildkit — Electron Control Center (separate from target application Electron main.js).
'use strict';
const {app, BrowserWindow, ipcMain, dialog} = require('electron');
const path = require('node:path');
const {spawn} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const actions = new Set(['scan','install','prepare','run-python','test','run-electron','portable','setup','setup-control']);
let mainWindow;
function isMainFrame(event) {
  return mainWindow && event.sender === mainWindow.webContents &&
    event.senderFrame === mainWindow.webContents.mainFrame;
}
function launchAction(action) {
  const ps = path.join(process.env.SystemRoot || 'C:\\Windows','System32','WindowsPowerShell','v1.0','powershell.exe');
  const script = path.join(root,'STARTEN.ps1');
  return new Promise((resolve,reject)=>{
    let settled=false;
    let child;
    try {
      child=spawn(ps,['-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',script,'-Action',action],{
        cwd:root,detached:true,windowsHide:false,stdio:'ignore',shell:false
      });
    } catch(error){reject(error);return;}
    child.once('error',error=>{if(!settled){settled=true;reject(error);}});
    child.once('spawn',()=>{
      if(settled)return;
      settled=true;
      child.unref();
      resolve({started:true,action,pid:child.pid});
    });
  });
}
app.whenReady().then(()=>{
  mainWindow = new BrowserWindow({width:1280,height:820,minWidth:900,minHeight:650,
    fullscreen:true,autoHideMenuBar:true,backgroundColor:'#080a14',show:false,
    webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,
      sandbox:true,nodeIntegration:false,webSecurity:true}});
  mainWindow.removeMenu();
  mainWindow.webContents.on('did-fail-load',(_event,code,description)=>{
    dialog.showErrorBox('Electron Control Center',`Renderer konnte nicht geladen werden (${code}): ${description}`);
    app.exit(1);
  });
  mainWindow.loadFile(path.join(__dirname,'index.html')).catch(error=>{
    dialog.showErrorBox('Electron Control Center',String(error));
    app.exit(1);
  });
  mainWindow.once('ready-to-show',()=>mainWindow.show());
  mainWindow.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  mainWindow.webContents.on('will-navigate',(event)=>event.preventDefault());
  mainWindow.webContents.on('before-input-event',(event,input)=>{
    if(input.type==='keyDown' && input.key==='F11') mainWindow.setFullScreen(!mainWindow.isFullScreen());
  });
});
ipcMain.handle('buildkit:action',(event,action)=>{
  if(!isMainFrame(event) || typeof action!=='string' || !actions.has(action))
    throw new Error('Nicht autorisierte Aktion');
  return launchAction(action);
});
ipcMain.handle('buildkit:quit',(event)=>{
  if(!isMainFrame(event)) throw new Error('Nicht autorisierter Aufruf');
  app.quit();
});
app.on('window-all-closed',()=>app.quit());
