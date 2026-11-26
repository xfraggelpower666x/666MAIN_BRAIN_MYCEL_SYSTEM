'use strict';
const {app,BrowserWindow,ipcMain,dialog}=require('electron');
const path=require('node:path'),fs=require('node:fs'),{spawn,execFile}=require('node:child_process'),{promisify}=require('node:util');
const {AUDIO,canonical,output,selected}=require('./contracts.cjs');
const {id3Fields}=require('./id3.cjs');
const {resolveLayout}=require('./source-layout.cjs');
const exec=promisify(execFile),root=path.resolve(__dirname,'..');
const workerRoot=app.isPackaged?path.join(process.resourcesPath,'workers'):root;
const {locate}=require('./portable-runtime.cjs');
let mp,djRoot,restore;
let python,ffmpeg,ffprobe;
const smoke=process.argv.includes('--lyvra-smoke');
let win,job=null,ready=false,folder=null;const approved=new Set();
function auth(e){if(!win||e.sender!==win.webContents||e.senderFrame!==win.webContents.mainFrame)throw Error('IPC nicht autorisiert')}
function handle(name,fn){ipcMain.handle('cc:'+name,(e,...args)=>{auth(e);if(!ready)throw Error('System nicht bereit');return fn(...args)})}
function send(data){if(win&&!win.isDestroyed())win.webContents.send('cc:event',data)}
function boot(text){if(win&&!win.isDestroyed())win.webContents.send('cc:boot',text)}
async function probe(command,args){return exec(command,args,{windowsHide:true,timeout:20000,maxBuffer:1024*1024})}
async function startup(){
 const started=Date.now();
 try{
  ({python,ffmpeg,ffprobe}=locate(app.isPackaged?process.resourcesPath:root,process.env,process.platform,app.isPackaged));
  const layout=resolveLayout(workerRoot);mp=layout.mp;djRoot=path.dirname(path.dirname(layout.dj));restore=path.dirname(layout.restore);
  await win.loadFile(path.join(root,'renderer','boot.html'),{query:{source:layout.mode}});win.show();
  boot('QUELLEN PRÜFEN: '+layout.mode);
  boot('PYTHON / DSP PRÜFEN');await probe(python,['-c','import mutagen, numpy, scipy, soundfile, pywt, pyloudnorm; from importlib.metadata import version; version("sounddevice")']);
  boot('FFMPEG / FFPROBE PRÜFEN');await probe(ffmpeg,['-version']);await probe(ffprobe,['-version']);
  boot('MP3 ENGINE PRÜFEN');const r=await exec(python,[path.join(workerRoot,'tools','probe_mp3.py'),mp],{windowsHide:true,timeout:20000});if(!r.stdout.includes('MP3_READY'))throw Error('MP3 Engine nicht bereit');
  boot('HUD INITIALISIEREN');await new Promise(r=>setTimeout(r,Math.max(0,8000-(Date.now()-started))));
  await win.loadFile(path.join(root,'renderer','index.html'));ready=true;
  if(smoke){const hud=await win.webContents.executeJavaScript("document.title==='LYVRA MP3 COMMAND CENTER' && !!document.querySelector('#choose') && !!document.querySelector('#restore')");if(!hud||!win.isVisible())throw Error('HUD nicht bereit');fs.writeFileSync(path.join(app.getPath('temp'),'lyvra-r032-'+process.pid+'.json'),JSON.stringify({status:'PASS',packaged:app.isPackaged,visible:win.isVisible(),workerRoot,python,ffmpeg,ffprobe}),{flag:'wx'});app.exit(0)}
 }catch(e){if(smoke){console.error(e);app.exit(1);return}if(!win.isVisible()){await win.loadFile(path.join(root,'renderer','boot.html'));win.show()}boot('START BLOCKIERT: '+e.message);dialog.showErrorBox('LYVRA Start blockiert',e.message)}
}
function run(module,script,args,data,keepStdin=false){
 if(job)throw Error('Ein Audioauftrag läuft bereits');
 const child=spawn(python,['-u',script,...args],{cwd:path.dirname(script),windowsHide:true,stdio:['pipe','pipe','pipe'],env:{...process.env,LYVRA_FFMPEG:ffmpeg,LYVRA_FFPROBE:ffprobe,PATH:path.dirname(ffmpeg)+path.delimiter+path.dirname(ffprobe)+path.delimiter+process.env.PATH,PYTHONUTF8:'1'}});
 job={child,module,keepStdin};let buffer='',failed=false;child.stdout.setEncoding('utf8');
 child.stdout.on('data',chunk=>{buffer+=chunk;if(buffer.length>8*1024*1024){failed=true;child.kill();return}let i;while((i=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,i);buffer=buffer.slice(i+1);try{send({module,data:JSON.parse(line)})}catch{send({module,data:{message:line.slice(0,1000)}})}}});
 child.stderr.on('data',c=>send({module,data:{message:c.toString().slice(0,1000)}}));
 child.stdin.on('error',()=>{});child.once('error',e=>{failed=true;send({module,data:{type:'error',message:e.message}})});
 child.once('close',code=>{if(job?.child===child)job=null;send({module,data:{type:'ended',code:failed?1:code}})});
 child.stdin.write(JSON.stringify(data)+'\n');if(!keepStdin)child.stdin.end();return true;
}
handle('choose',async()=>{const r=await dialog.showOpenDialog(win,{properties:['openFile','multiSelections'],filters:[{name:'Audio',extensions:[...AUDIO].map(x=>x.slice(1))}]});if(r.canceled)return [];const files=r.filePaths.map(canonical).filter(p=>AUDIO.has(path.extname(p).toLowerCase())&&fs.statSync(p).isFile());files.forEach(p=>approved.add(p));return files});
handle('folder',async()=>{if(job)throw Error('Auftrag läuft');const r=await dialog.showOpenDialog(win,{properties:['openDirectory','createDirectory']});if(!r.canceled)folder=canonical(r.filePaths[0]);return folder});
handle('start',req=>{
 if(!req||!Array.isArray(req.files)||!req.files.length||req.files.length>5000)throw Error('Keine gültige Auswahl');
 const files=[...new Set(req.files.map(f=>selected(f,approved)))],source=files[0];
 if(req.action==='inspect')return run('mp3',mp,[],{action:'inspect',source},true);
 if(!folder)throw Error('Ausgabeordner auswählen');
 if(req.action==='metadata'){if(path.extname(source).toLowerCase()!=='.mp3')throw Error('MP3 erforderlich');const fields=id3Fields(req.fields);return run('mp3',mp,[],{action:'metadata_copy',source,destination:output(folder,req.name,'.mp3'),fields},true)}
 if(req.action==='convert'){const ext=path.extname(req.name).toLowerCase();if(!['.mp3','.wav'].includes(ext))throw Error('Format nicht erlaubt');return run('mp3',mp,[],{action:'export',source,destination:output(folder,req.name,ext),stream:Number.isInteger(req.stream)&&req.stream>=0?req.stream:0},true)}
 if(req.action==='dj')return run('dj',path.join(djRoot,'engine','worker.py'),['--input-json','-','--ffmpeg',ffmpeg,'--ffprobe',ffprobe],{files,output:folder,profile:['stream','dj','custom'].includes(req.profile)?req.profile:'stream',bitrate:req.bitrate===320?320:256,export_m3u:!!req.m3u,block_mode:false,write_metadata:false,rotate_covers:false,export_stream_ready:false});
 if(req.action==='restore'){if(!['.wav','.mp3'].includes(path.extname(source).toLowerCase()))throw Error('Restoration benötigt WAV oder MP3; zuerst konvertieren');if(!['Off','STFT','Wavelet','Both'].includes(req.mode))throw Error('DSP-Modus ungültig');return run('restore',path.join(workerRoot,'tools','restore_worker.py'),[],{source,destination:output(folder,req.name,'.wav'),mode:req.mode,engine:restore})}
 throw Error('Unbekannte Aktion');
});
handle('stop',()=>{if(!job)return false;if(!job.keepStdin)throw Error('Sicherer Abbruch für dieses Modul noch nicht integriert');job.child.stdin.write('CANCEL\n');return true});
app.whenReady().then(()=>{win=new BrowserWindow({show:false,fullscreen:true,backgroundColor:'#08090f',autoHideMenuBar:true,webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,sandbox:true,nodeIntegration:false,webSecurity:true}});win.removeMenu();win.webContents.setWindowOpenHandler(()=>({action:'deny'}));win.webContents.on('will-navigate',e=>e.preventDefault());win.on('close',e=>{if(job){e.preventDefault();dialog.showMessageBox(win,{message:'Audioauftrag läuft. Bitte Abschluss abwarten oder MP3-Auftrag stoppen.'})}});startup()});
app.on('window-all-closed',()=>app.quit());
