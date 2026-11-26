'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {verify}=require('../electron/verify-build-inputs.cjs');
function fixture(){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cb-release-gate-'));
 const pkg={name:'666-chatbackup-electron-shell',version:'0.1.0',devDependencies:{electron:'^33.4.11','electron-builder':'^25.1.8'}};
 fs.writeFileSync(path.join(dir,'package.json'),JSON.stringify(pkg));
 const lock={name:pkg.name,version:pkg.version,lockfileVersion:3,packages:{'':{name:pkg.name,version:pkg.version,devDependencies:pkg.devDependencies}}};
 fs.writeFileSync(path.join(dir,'package-lock.json'),JSON.stringify(lock));
 fs.mkdirSync(path.join(dir,'node_modules','electron'),{recursive:true});
 fs.mkdirSync(path.join(dir,'node_modules','.bin'),{recursive:true});
 fs.writeFileSync(path.join(dir,'node_modules','electron','package.json'),'{}');
 fs.writeFileSync(path.join(dir,'node_modules','.bin','electron-builder.cmd'),'');
 return {dir,lock};
}
test('valid frozen build inputs accepted, and missing lock rejected',()=>{
 const f=fixture();try{assert.equal(verify(f.dir).ok,true);fs.unlinkSync(path.join(f.dir,'package-lock.json'));assert.throws(()=>verify(f.dir),/Lockfile|package-lock/)}finally{fs.rmSync(f.dir,{recursive:true,force:true})}
});
test('dependency drift and missing binary runner rejected',()=>{
 const f=fixture();try{
 f.lock.packages[''].devDependencies.electron='^99.0.0';fs.writeFileSync(path.join(f.dir,'package-lock.json'),JSON.stringify(f.lock));assert.throws(()=>verify(f.dir),/Versionsbereich/);
 f.lock.packages[''].devDependencies.electron='^33.4.11';fs.writeFileSync(path.join(f.dir,'package-lock.json'),JSON.stringify(f.lock));fs.unlinkSync(path.join(f.dir,'node_modules','.bin','electron-builder.cmd'));assert.throws(()=>verify(f.dir),/electron-builder.cmd/);
 }finally{fs.rmSync(f.dir,{recursive:true,force:true})}
});
