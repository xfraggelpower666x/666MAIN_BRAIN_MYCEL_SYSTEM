'use strict';
const {app,BrowserWindow,ipcMain,dialog}=require('electron');
const path=require('path'),fs=require('fs'),{spawn}=require('child_process');
let mainWindow,monitorWindow,job,approved=new Set(),approvedOutputDir=null;
function isAuthorized(event){
  const id=event.sender.id;
  if(![mainWindow,monitorWindow].some(w=>w&&!w.isDestroyed()&&w.webContents.id===id) || event.senderFrame!==event.sender.mainFrame) throw Error('IPC denied');
}
function roots(){return app.isPackaged ? {worker:path.join(process.resourcesPath,'engine_bridge.py'),original:path.join(process.resourcesPath,'lyvra-original')} : {worker:path.join(__dirname,'..','engine_bridge.py'),original:path.join(__dirname,'..','..','L.Y.V.R.A._MP3_MANAGER')};}
function isApproved(file){return typeof file==='string' && approved.has(path.resolve(file));}
function broadcast(topic,payload){for(const w of [mainWindow,monitorWindow])if(w&&!w.isDestroyed())w.webContents.send(topic,payload);}
function makeWindow(monitor=false){const win=new BrowserWindow({width:monitor?570:1440,height:monitor?420:920,minWidth:monitor?380:980,minHeight:monitor?220:620,backgroundColor:'#080914',title:monitor?'LYVRA · STATUS MONITOR':'L.Y.V.R.A. · MP3 MANAGER',webPreferences:{preload:path.join(__dirname,'preload.cjs'),nodeIntegration:false,contextIsolation:true,sandbox:true,webSecurity:true}});win.loadFile(path.join(__dirname,'..','renderer',monitor?'monitor.html':'index.html'));win.webContents.setWindowOpenHandler(()=>({action:'deny'}));win.webContents.on('will-navigate',(e,url)=>{if(url!==win.webContents.getURL())e.preventDefault()});if(!monitor)win.maximize();return win;}
app.whenReady().then(()=>{mainWindow=makeWindow();app.on('activate',()=>{if(!BrowserWindow.getAllWindows().length)mainWindow=makeWindow()})});
app.on('window-all-closed',()=>{if(process.platform!=='darwin')app.quit()});
app.on('before-quit',()=>{if(job)try{job.stdin.write('CANCEL\n')}catch{}});
ipcMain.handle('lyvra:choose',async(e,kind)=>{isAuthorized(e);if(job)throw Error('Auftrag läuft');const folder=kind==='folder';const opts={properties:folder?['openDirectory']:['openFile','multiSelections'],filters:folder?undefined:[{name:'Audio/Video',extensions:['mp3','wav','mp4','mkv','m4a','flac','ogg','aac','webm']}]};const answer=await dialog.showOpenDialog(mainWindow,opts);if(answer.canceled)return [];
  if(folder){approvedOutputDir=path.resolve(answer.filePaths[0]);return [approvedOutputDir]}
  const paths=answer.filePaths.map(p=>path.resolve(p));paths.forEach(p=>approved.add(p));return paths;
});
ipcMain.handle('lyvra:scan',async(e,dir)=>{isAuthorized(e);if(typeof dir!=='string'||path.resolve(dir)!==approvedOutputDir)throw Error('Ordner nicht autorisiert');let files=fs.readdirSync(dir,{withFileTypes:true}).filter(d=>d.isFile()&&/\.(mp3|wav|mp4|mkv|m4a|flac|ogg|aac|webm)$/i.test(d.name)).slice(0,5000).map(d=>{let p=path.join(dir,d.name);approved.add(path.resolve(p));return {path:p,name:d.name,bytes:fs.statSync(p).size}});return files});
ipcMain.handle('lyvra:monitor',e=>{isAuthorized(e);if(!monitorWindow||monitorWindow.isDestroyed())monitorWindow=makeWindow(true);else monitorWindow.focus();return true});
ipcMain.handle('lyvra:check',e=>{isAuthorized(e);return {mode:app.isPackaged?'packaged':'development',worker:roots().worker,python:(process.env.LYVRA_PYTHON||'python'),backendRuntime:'Host Python required; not bundled in Electron candidate'}});
ipcMain.handle('lyvra:start',async(e,req)=>{isAuthorized(e);if(job)throw Error('Auftrag läuft');if(!req||!['inspect','export','check','metadata_copy'].includes(req.action))throw Error('Ungültige Aktion');if(req.action!=='check'&&!isApproved(req.source))throw Error('Quelle nicht ausgewählt');
 if(req.action==='export'||req.action==='metadata_copy'){
   if(!approvedOutputDir)throw Error('Zielordner auswählen');
   if(!['.mp3','.wav','.mp4'].includes(path.extname(req.destination).toLowerCase()))throw Error('Zielformat gesperrt');
   if(path.resolve(path.dirname(req.destination))!==approvedOutputDir)throw Error('Zielpfad nicht autorisiert');
   if(fs.existsSync(req.destination)||(()=>{try{fs.lstatSync(req.destination);return true}catch(e){if(e.code==='ENOENT')return false;throw e}})())throw Error('Ausgabe existiert bereits');
   if(req.action==='metadata_copy'&&(path.extname(req.source).toLowerCase()!=='.mp3'||path.extname(req.destination).toLowerCase()!=='.mp3'||!req.fields||typeof req.fields!=='object'||Array.isArray(req.fields)))throw Error('Ungültige Metadatenbearbeitung');
   if(!Array.isArray(req.images||[])||(req.images||[]).some(p=>!isApproved(p)))throw Error('Bilder nicht autorisiert');
 }
 const python=process.env.LYVRA_PYTHON||'python';
 const child=spawn(python,['-u',roots().worker],{cwd:path.dirname(roots().worker),windowsHide:true,stdio:['pipe','pipe','pipe'],env:{...process.env,PYTHONUTF8:'1'}});
 job=child;let buffer='',errs='',finished=false;
 child.stdout.setEncoding('utf8');child.stdout.on('data',part=>{buffer+=part;if(buffer.length>8*1024*1024){child.kill();return}let i;while((i=buffer.indexOf('\n'))!==-1){const line=buffer.slice(0,i);buffer=buffer.slice(i+1);try{const message=JSON.parse(line);broadcast('lyvra:status',message)}catch{broadcast('lyvra:status',{type:'error',message:'Ungültige Worker-Antwort'})}}});
 child.stderr.setEncoding('utf8');child.stderr.on('data',chunk=>{errs=(errs+chunk).slice(-1500)});
 child.on('error',ex=>{broadcast('lyvra:status',{type:'error',message:ex.message})});
 child.on('close',code=>{if(job===child)job=null;broadcast('lyvra:status',{type:'ended',code,stderr:code?errs:''})});
 child.stdin.write(JSON.stringify(req)+'\n');
 return {started:true};
});
ipcMain.handle('lyvra:stop',e=>{isAuthorized(e);if(!job)return false;try{job.stdin.write('CANCEL\n');return true}catch{return false}});
