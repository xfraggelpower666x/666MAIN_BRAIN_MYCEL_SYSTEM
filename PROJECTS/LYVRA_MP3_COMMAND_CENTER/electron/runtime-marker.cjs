'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
function repairMarker(root,repair=false){
 const pkg=path.join(root,'node_modules','electron'),exe=path.join(pkg,'dist','electron.exe'),marker=path.join(pkg,'path.txt');
 const version=JSON.parse(fs.readFileSync(path.join(pkg,'package.json'),'utf8')).version;
 if(!/^\d+\.\d+\.\d+$/.test(version))throw Error('Ungültige Electron-Version');
 if(!fs.statSync(exe).isFile()||fs.statSync(exe).size<=1000000)throw Error('Electron-Runtime fehlt oder ist unvollständig');
 const previous=fs.existsSync(marker)?fs.readFileSync(marker):null;
 if(previous?.equals(Buffer.from('electron.exe')))return {exe,changed:false};
 if(!repair)throw Error('path.txt benötigt explizite Reparatur');
 const suffix=crypto.randomUUID();if(previous)fs.writeFileSync(marker+'.before-'+suffix,previous,{flag:'wx'});
 const tmp=marker+'.tmp-'+suffix;try{fs.writeFileSync(tmp,'electron.exe',{encoding:'ascii',flag:'wx'});fs.renameSync(tmp,marker)}finally{fs.rmSync(tmp,{force:true})}
 return {exe,changed:true};
}
module.exports={repairMarker};
if(require.main===module){try{console.log(JSON.stringify(repairMarker(path.resolve(__dirname,'..'),process.argv.includes('--repair'))))}catch(e){console.error(e.message);process.exitCode=1}}
