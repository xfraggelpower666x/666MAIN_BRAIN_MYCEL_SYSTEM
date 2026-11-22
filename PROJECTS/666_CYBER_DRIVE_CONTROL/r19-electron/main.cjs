'use strict';
const {app, BrowserWindow, ipcMain, Tray, Menu, nativeImage} = require('electron');
const {spawn} = require('node:child_process');
const path = require('node:path');
let mainWindow = null, overlay = null, tray = null, worker = null, pending = '';
let latest = {protocol:'cyber-drive.metrics.v2',status:'starting', volumes:[], timestamp:null, error:null};
const send = () => { for (const w of [mainWindow, overlay]) if (w && !w.isDestroyed()) w.webContents.send('metrics', latest); };
function createWindow() {
  mainWindow = new BrowserWindow({width:1250,height:820,minWidth:800,minHeight:500,backgroundColor:'#11141A',
    webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  mainWindow.loadFile(path.join(__dirname,'index.html'));
  mainWindow.on('closed',()=>{mainWindow=null;});
}
function toggleOverlay() {
  if (overlay && !overlay.isDestroyed()) {overlay.close();overlay=null;return;}
  overlay = new BrowserWindow({width:580,height:100,minWidth:190,minHeight:70,frame:false,transparent:true,
    alwaysOnTop:true,skipTaskbar:true,resizable:true,webPreferences:{preload:path.join(__dirname,'preload.cjs'),
    contextIsolation:true,nodeIntegration:false,sandbox:true}});
  overlay.loadFile(path.join(__dirname,'index.html'),{query:{overlay:'1'}});
  overlay.on('closed',()=>{overlay=null;});
}
function startSampler() {
  const requested=process.env.KLRW_PYTHON;
  const exe=requested || (process.platform==='win32'?'py':'python3');
  const args=requested?['-u',path.join(__dirname,'bridge','volume_metrics.py')]:
    (process.platform==='win32'?['-3.13','-u',path.join(__dirname,'bridge','volume_metrics.py')]:
      ['-u',path.join(__dirname,'bridge','volume_metrics.py')]);
  try {
    worker=spawn(exe,args,{windowsHide:true,stdio:['ignore','pipe','pipe'],env:{...process.env,PYTHONUNBUFFERED:'1'}});
    worker.stdout.setEncoding('utf8');
    worker.stdout.on('data',chunk=>{
      pending += chunk;
      if(pending.length>1048576){pending='';latest={status:'error',volumes:[],error:'Metrics stream over limit'};send();return;}
      let ix;
      while((ix=pending.indexOf('\n'))!==-1){
        const line=pending.slice(0,ix); pending=pending.slice(ix+1);
        try {const data=JSON.parse(line);if(data&&Array.isArray(data.volumes) && data.protocol === 'cyber-drive.metrics.v2'&&typeof data.status==='string'){latest=data;send();}}catch{}
      }
    });
    let stderr='';
    worker.stderr.setEncoding('utf8');
    worker.stderr.on('data',s=>{stderr=(stderr+s).slice(-1800);});
    worker.on('error',e=>{latest={status:'error',volumes:[],error:e.message};send();});
    worker.on('exit',(code)=>{worker=null;latest={status:'stopped',volumes:[],error:stderr || ('Metrics worker exited: '+code)};send();});
  } catch(e) {latest={status:'error',volumes:[],error:e.message};send();}
}
function startTray(){
  // A visible tray icon is not promised on a headless environment. Never fake its status.
  try {
    const pix=Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000b49444154789c636000020000050001a5f645400000000049454e44ae426082','hex');
    tray=new Tray(nativeImage.createFromBuffer(pix));
    tray.setToolTip('666 Cyber Drive Control — R19');
    tray.setContextMenu(Menu.buildFromTemplate([
      {label:'Show D Dashboard',click:()=>{if(!mainWindow)createWindow();mainWindow.show();mainWindow.focus();}},
      {label:'Toggle overlay',click:toggleOverlay},
      {type:'separator'}, {label:'Exit',click:()=>app.quit()}
    ]));
    tray.on('double-click',()=>{if(mainWindow)mainWindow.show();});
  }catch(e){latest.error='Tray unavailable: '+e.message;}
}
ipcMain.handle('get-latest',()=>latest);
ipcMain.handle('overlay-toggle',()=>{toggleOverlay();return Boolean(overlay);});
ipcMain.handle('show-main',()=>{if(mainWindow)mainWindow.show();});
app.whenReady().then(()=>{createWindow();startTray();startSampler();});
app.on('window-all-closed',()=>{/* tray app continues until explicit Exit */});
app.on('before-quit',()=>{if(worker){worker.kill();worker=null;}if(tray){tray.destroy();tray=null;}});
