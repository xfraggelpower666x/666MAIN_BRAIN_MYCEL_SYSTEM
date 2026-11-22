'use strict';
const {app,BrowserWindow,dialog,ipcMain}=require('electron');
const path=require('path'),fs=require('fs'),{spawn}=require('child_process');
const allowed=new Set(['.mp3','.wav','.flac','.ogg','.m4a','.aac','.aiff','.wma']);
let windowRef=null,job=null;
const res=p=>app.isPackaged?path.join(process.resourcesPath,p):path.join(__dirname,'..',p);
function validated(paths){return [...new Set((Array.isArray(paths)?paths:[]).filter(p=>typeof p==='string'&&allowed.has(path.extname(p).toLowerCase())&&fs.existsSync(p)&&fs.statSync(p).isFile()))];}
function emit(type,data){if(windowRef&&!windowRef.isDestroyed())windowRef.webContents.send('job:event',{type,data});}
app.whenReady().then(()=>{
 windowRef=new BrowserWindow({width:1250,height:840,minWidth:960,minHeight:650,backgroundColor:'#101019',webPreferences:{preload:path.join(__dirname,'preload.js'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
 windowRef.loadFile(path.join(__dirname,'index.html'));windowRef.webContents.setWindowOpenHandler(()=>({action:'deny'}));
});
app.on('window-all-closed',()=>{if(process.platform!=='darwin')app.quit();});
ipcMain.handle('files:choose',async()=>{const r=await dialog.showOpenDialog(windowRef,{properties:['openFile','multiSelections']});return r.canceled?[]:validated(r.filePaths);});
ipcMain.handle('files:validate',(_,a)=>validated(a));
ipcMain.handle('folder:choose',async()=>{const r=await dialog.showOpenDialog(windowRef,{properties:['openDirectory','createDirectory']});return r.canceled?null:r.filePaths[0];});
ipcMain.handle('job:start',async(_,p)=>{
 if(job)return {ok:false,error:'Auftrag läuft bereits'};
 const files=validated(p?.files),output=p?.output;
 if(!files.length||typeof output!=='string'||!fs.existsSync(output)||!fs.statSync(output).isDirectory())return {ok:false,error:'Dateien oder Ziel fehlen'};
 const profile=['stream','dj','custom'].includes(p.profile)?p.profile:'stream';
 const cmd=app.isPackaged?res('engine/autodj-engine.exe'):(process.platform==='win32'?'py':'python3');
 const args=app.isPackaged?[]:['-u',res('engine/worker.py')];
 args.push('--input-json','-','--ffmpeg',app.isPackaged?res('ffmpeg/ffmpeg.exe'):(process.env.AUTO_DJ_FFMPEG||'ffmpeg'));
 try{
  const proc=spawn(cmd,args,{stdio:['pipe','pipe','pipe'],windowsHide:true});job=proc;
  let pending='';proc.stdout.on('data',chunk=>{pending+=chunk.toString();let lines=pending.split(/\r?\n/);pending=lines.pop();for(const line of lines){try{emit('progress',JSON.parse(line));}catch{emit('message',line);}}});
  proc.stderr.on('data',chunk=>emit('message',chunk.toString().slice(0,500)));
  proc.once('error',err=>{emit('error',err.message);if(job===proc)job=null;});
  proc.once('close',code=>{emit('finished',{code});if(job===proc)job=null;});
  proc.stdin.end(JSON.stringify({files,output,profile,bitrate:p.bitrate===320?320:256,export_m3u:p.export_m3u===true})+'\n');
  return {ok:true};
 }catch(err){job=null;return {ok:false,error:err.message};}
});
ipcMain.handle('job:cancel',()=>{if(!job)return false;if(process.platform==='win32')spawn('taskkill',['/PID',String(job.pid),'/T','/F'],{windowsHide:true});else job.kill('SIGTERM');return true;});
