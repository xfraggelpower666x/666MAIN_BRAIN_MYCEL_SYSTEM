'use strict';
const {app, BrowserWindow, ipcMain, Tray, Menu, nativeImage} = require('electron');
const {spawn} = require('node:child_process');
const path = require('node:path');
const {createStore} = require('./app-settings-store.cjs');
let mainWindow = null, overlay = null, tray = null, worker = null, pending = '';
let settingsWindow = null, settingsStore = null, appSettings = null;
const pendingReplies = new Map();
let nextRequestId = 0;
let latest = {protocol:'cyber-drive.metrics.v2',status:'starting', volumes:[], timestamp:null, error:null};
function processReply(data) {
  const r=pendingReplies.get(data.request_id);
  if(!r)return;
  clearTimeout(r.timer);pendingReplies.delete(data.request_id);
  r.resolve({ok:data.ok===true,error:typeof data.error==='string'?data.error:null});
}
function workspaceCommand(action,payload) {
  if(!['set-drive-visibility','set-overlay-layout','set-visual-binding'].includes(action))
    return Promise.resolve({ok:false,error:'Unsupported action'});
  if(!worker||!worker.stdin?.writable)
    return Promise.resolve({ok:false,error:'Metrics bridge not running'});
  return new Promise(resolve=>{
    const id=++nextRequestId;
    const timer=setTimeout(()=>{pendingReplies.delete(id);resolve({ok:false,error:'Command timeout'});},5000);
    pendingReplies.set(id,{resolve,timer});
    worker.stdin.write(JSON.stringify({...payload,action,request_id:id})+'\n',err=>{
      if(err&&pendingReplies.has(id)){clearTimeout(timer);pendingReplies.delete(id);resolve({ok:false,error:'Bridge pipe error'});}
    });
  });
}
const send = () => { for (const w of [mainWindow, overlay]) if (w && !w.isDestroyed()) w.webContents.send('metrics', latest); };
function settingsSender(event){
  return settingsWindow&&!settingsWindow.isDestroyed()&&event.sender===settingsWindow.webContents&&
    event.senderFrame===settingsWindow.webContents.mainFrame;
}
function openSettings(){
  if(settingsWindow&&!settingsWindow.isDestroyed()){settingsWindow.focus();return;}
  settingsWindow=new BrowserWindow({width:690,height:520,minWidth:540,minHeight:440,show:false,
    parent:mainWindow||undefined,backgroundColor:'#0b0c1b',autoHideMenuBar:true,
    webPreferences:{preload:path.join(__dirname,'app-settings-preload.cjs'),contextIsolation:true,
      nodeIntegration:false,sandbox:true,webSecurity:true}});
  settingsWindow.removeMenu();
  settingsWindow.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  settingsWindow.webContents.on('will-navigate',e=>e.preventDefault());
  settingsWindow.loadFile(path.join(__dirname,'app-settings','settings.html')).catch(e=>{settingsWindow?.close();});
  settingsWindow.once('ready-to-show',()=>settingsWindow.show());
  settingsWindow.on('closed',()=>{settingsWindow=null;});
}
ipcMain.handle('app-settings:load',event=>{
  if(!settingsSender(event))throw new Error('Unauthorized settings sender');
  return {...appSettings};
});
ipcMain.handle('app-settings:save',(event,value)=>{
  if(!settingsSender(event))throw new Error('Unauthorized settings sender');
  const saved=settingsStore.save(value);appSettings=saved;
  if(mainWindow&&!mainWindow.isDestroyed())mainWindow.setFullScreen(saved.fullscreen);
  return {...saved};
});
ipcMain.handle('app-settings:open',event=>{
  if(!mainWindow||mainWindow.isDestroyed()||event.sender!==mainWindow.webContents||
     event.senderFrame!==mainWindow.webContents.mainFrame)throw new Error('Unauthorized settings open');
  openSettings();return true;
});
function createWindow() {
  mainWindow = new BrowserWindow({width:1250,height:820,minWidth:800,minHeight:500,
    fullscreen:appSettings?.fullscreen===true,backgroundColor:'#11141A',
    webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  mainWindow.webContents.on('before-input-event',(event,input)=>{
    if(input.type!=='keyDown'||input.isAutoRepeat)return;
    if(input.key==='F10'||(input.control&&input.key===',')){event.preventDefault();openSettings();}
    else if(input.key==='F11'){
      event.preventDefault();const next=!mainWindow.isFullScreen();
      const saved=settingsStore.save({...appSettings,fullscreen:next});appSettings=saved;
      mainWindow.setFullScreen(next);
    }
  });
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
  // Packaged releases run ONLY the embedded, independently frozen Python engine.
  // Development runs the same bridge through the selected Python 3.13 interpreter.
  const packaged = app.isPackaged;
  const requested = process.env.KLRW_PYTHON;
  const exe = packaged ? path.join(process.resourcesPath,'engine','666CyberMetrics.exe') :
    (requested || (process.platform==='win32'?'py':'python3'));
  const args = packaged ? [] : requested ?
    ['-u',path.join(__dirname,'bridge','volume_metrics.py')] :
    (process.platform==='win32'?['-3.13','-u',path.join(__dirname,'bridge','volume_metrics.py')]:
      ['-u',path.join(__dirname,'bridge','volume_metrics.py')]);
  try {
    worker=spawn(exe,args,{windowsHide:true,stdio:['pipe','pipe','pipe'],env:{...process.env,PYTHONUNBUFFERED:'1'}});
    worker.stdout.setEncoding('utf8');
    worker.stdout.on('data',chunk=>{
      pending += chunk;
      if(pending.length>1048576){pending='';latest={status:'error',volumes:[],error:'Metrics stream over limit'};send();return;}
      let ix;
      while((ix=pending.indexOf('\n'))!==-1){
        const line=pending.slice(0,ix); pending=pending.slice(ix+1);
        try {const data=JSON.parse(line);if(data?.type==='reply'){processReply(data);continue;}if(data&&Array.isArray(data.volumes) && data.protocol === 'cyber-drive.metrics.v2'&&typeof data.status==='string'){latest=data;send();}}catch{}
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
ipcMain.handle('set-drive-visibility',(_e,id,target,enabled)=>{
  if(typeof id!=='string'||!id||id.length>512||!['tray','overlay'].includes(target)||typeof enabled!=='boolean')
    return {ok:false,error:'Invalid visibility request'};
  return workspaceCommand('set-drive-visibility',{volume_id:id,target,enabled});
});
ipcMain.handle('set-overlay-layout',(_e,layout)=>{
  if(!['minimal','horizontal','vertical'].includes(layout))return {ok:false,error:'Invalid layout'};
  return workspaceCommand('set-overlay-layout',{layout});
});
ipcMain.handle('set-visual-binding',(_event,led,device,mode,threshold_kib)=>{
  if(!['caps','num','scroll'].includes(led)||typeof device!=='string'||!device||device.length>256||
     !['off','read','write','either'].includes(mode)||typeof threshold_kib!=='number'||
     !Number.isFinite(threshold_kib)||threshold_kib<0||threshold_kib>1048576)
    return {ok:false,error:'Invalid visual LED binding'};
  return workspaceCommand('set-visual-binding',{led,device,mode,threshold_kib});
});
ipcMain.handle('overlay-toggle',()=>{toggleOverlay();return Boolean(overlay);});
ipcMain.handle('show-main',()=>{if(mainWindow)mainWindow.show();});
app.whenReady().then(()=>{settingsStore=createStore(app.getPath('userData'));appSettings=settingsStore.load();createWindow();startTray();startSampler();});
app.on('window-all-closed',()=>{/* tray app continues until explicit Exit */});
app.on('before-quit',()=>{if(settingsWindow&&!settingsWindow.isDestroyed())settingsWindow.close();if(worker){worker.kill();worker=null;}if(tray){tray.destroy();tray=null;}});
