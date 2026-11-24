'use strict';
const {app,BrowserWindow,dialog,ipcMain}=require('electron');
const fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const extensions=new Set(['.mp3','.wav','.flac','.ogg','.m4a','.aac','.aiff','.wma']);
let windowRef=null,job=null;
const resource=p=>app.isPackaged?path.join(process.resourcesPath,p):path.join(__dirname,'..',p);
function validated(paths){return [...new Set((Array.isArray(paths)?paths:[]).filter(p=>typeof p==='string'&&extensions.has(path.extname(p).toLowerCase())&&fs.existsSync(p)&&fs.statSync(p).isFile()))];}
function emit(type,data){if(windowRef&&!windowRef.isDestroyed())windowRef.webContents.send('job:event',{type,data});}
app.whenReady().then(()=>{windowRef=new BrowserWindow({width:1260,height:830,minWidth:960,minHeight:650,backgroundColor:'#101019',webPreferences:{preload:path.join(__dirname,'preload.js'),contextIsolation:true,nodeIntegration:false,sandbox:true}});windowRef.loadFile(path.join(__dirname,'index.html'));windowRef.webContents.setWindowOpenHandler(()=>({action:'deny'}));});
app.on('window-all-closed',()=>{if(process.platform!=='darwin')app.quit();});
ipcMain.handle('files:choose',async()=>{const res=await dialog.showOpenDialog(windowRef,{properties:['openFile','multiSelections']});return res.canceled?[]:validated(res.filePaths);});
ipcMain.handle('files:validate',(_,a)=>validated(a));
ipcMain.handle('folder:choose',async()=>{const res=await dialog.showOpenDialog(windowRef,{properties:['openDirectory','createDirectory']});return res.canceled?null:res.filePaths[0];});
ipcMain.handle('job:start',async(_,input)=>{
 if(job)return {ok:false,error:'A render is already running'};
 const files=validated(input?.files),output=input?.output;
 if(!files.length||typeof output!=='string'||!fs.existsSync(output)||!fs.statSync(output).isDirectory())return {ok:false,error:'Missing input files or output directory'};
 const cmd=app.isPackaged?resource('engine/autodj-engine.exe'):(process.platform==='win32'?'python':'python3');
 const args=app.isPackaged?[]:['-u',resource('engine/worker.py')];
 args.push('--input-json','-','--ffmpeg',app.isPackaged?resource('ffmpeg/ffmpeg.exe'):resource('tools/ffmpeg/ffmpeg.exe'),'--ffprobe',app.isPackaged?resource('ffmpeg/ffprobe.exe'):resource('tools/ffmpeg/ffprobe.exe'));
 const data={files,output,profile:['stream','dj','custom'].includes(input.profile)?input.profile:'stream',bitrate:input.bitrate===320?320:256,block_mode:input.block_mode===true,hardcore:input.hardcore===true,export_m3u:input.export_m3u===true,split_mode:['MINUTES','TRACKS','HYBRID'].includes(input.split_mode)?input.split_mode:'MINUTES',target_minutes:Number.isInteger(input.target_minutes)?input.target_minutes:180,target_tracks:Number.isInteger(input.target_tracks)?input.target_tracks:40,
 write_metadata:input.write_metadata===true,rotate_covers:input.rotate_covers===true,
 cover_dir:typeof input.cover_dir==='string'&&fs.existsSync(input.cover_dir)&&fs.statSync(input.cover_dir).isDirectory()?input.cover_dir:resource('legacy/covers'),
 export_stream_ready:input.export_stream_ready===true,metadata_profile_path:resource('legacy/metadata.json')};
 try{const child=spawn(cmd,args,{stdio:['pipe','pipe','pipe'],windowsHide:true});job=child;let pending='';child.stdout.on('data',c=>{pending+=c.toString();const lines=pending.split(/\r?\n/);pending=lines.pop();for(const line of lines){try{emit('progress',JSON.parse(line));}catch{emit('message',line);}}});child.stderr.on('data',c=>emit('message',c.toString().slice(0,1000)));child.once('error',e=>{emit('error',e.message);if(job===child)job=null;});child.once('close',code=>{emit('finished',{code});if(job===child)job=null;});child.stdin.end(JSON.stringify(data)+'\n');return {ok:true};}catch(e){job=null;return {ok:false,error:e.message};}
});
ipcMain.handle('job:abort',()=>{if(!job)return false;const child=job;if(process.platform==='win32')spawn('taskkill',['/PID',String(child.pid),'/T','/F'],{windowsHide:true});else child.kill('SIGTERM');return true;});
