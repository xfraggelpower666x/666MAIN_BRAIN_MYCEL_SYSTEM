'use strict';
// Release-only, read-only checks. Keep dev start independent of npm lockfile.
const fs=require('node:fs');
const path=require('node:path');
function verify(root){
  const pkg=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
  const lockpath=path.join(root,'package-lock.json');
  if(!fs.existsSync(lockpath))throw new Error('Electron package-lock.json fehlt: npm install mit Freigabe ausführen, danach Lockfile kontrollieren');
  const lock=JSON.parse(fs.readFileSync(lockpath,'utf8'));
  if(!Number.isInteger(lock.lockfileVersion)||lock.lockfileVersion<2)throw new Error('Ungültiges oder veraltetes npm Lockfile');
  const installed=lock.packages&&lock.packages[''];
  if(!installed)throw new Error('npm Lockfile: Root-Paket fehlt');
  if(lock.name!==pkg.name || installed.name && installed.name!==pkg.name)throw new Error('npm Lockfile: Paketname ungleich package.json');
  if(lock.version!==pkg.version || installed.version!==pkg.version)throw new Error('npm Lockfile: Projektversion weicht ab');
  for(const key of ['dependencies','devDependencies','optionalDependencies']){
    const expected=pkg[key]||{},actual=installed[key]||{};
    if(JSON.stringify(Object.keys(expected).sort())!==JSON.stringify(Object.keys(actual).sort()))throw new Error('npm Lockfile: '+key+' Abhängigkeiten unterschiedlich');
    for(const [name,range] of Object.entries(expected))if(actual[name]!==range)throw new Error('npm Lockfile: '+name+' Versionsbereich unterschiedlich');
  }
  if(!fs.existsSync(path.join(root,'node_modules','electron','package.json')))throw new Error('Electron npm Paket fehlt: npm ci ausführen');
  if(!fs.existsSync(path.join(root,'node_modules','.bin','electron-builder.cmd')))throw new Error('electron-builder.cmd fehlt: npm ci ausführen');
  return {ok:true,project:pkg.name,version:pkg.version};
}
if(require.main===module){try{console.log('[BUILD INPUT PASS]',verify(__dirname));}catch(e){console.error('[BUILD INPUT BLOCKED]',e.message);process.exitCode=1}}
module.exports={verify};
