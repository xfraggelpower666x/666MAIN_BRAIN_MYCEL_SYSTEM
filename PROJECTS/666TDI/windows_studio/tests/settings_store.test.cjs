'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {createStore,validate,DEFAULTS}=require('../electron/settings-store.cjs');
test('application settings default to fullscreen, independent of compiler',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'666-buildkit-settings-'));
 try{assert.deepEqual(createStore(dir).load(),DEFAULTS);assert.equal(fs.existsSync(path.join(dir,'settings.json')),false)}finally{fs.rmSync(dir,{recursive:true,force:true})}
});
test('full-screen and language preferences persist between instances',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'666-buildkit-settings-'));
 try{
  const a=createStore(dir);
  assert.deepEqual(a.save({fullscreen:false,language:'en',theme:'cyber'}),{fullscreen:false,language:'en',theme:'cyber'});
  assert.deepEqual(createStore(dir).load(),{fullscreen:false,language:'en',theme:'cyber'});
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
test('rejects unrecognized settings and invalid type without modifying stored state',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'666-buildkit-settings-'));
 try{
  const s=createStore(dir);s.save({fullscreen:true});
  const before=fs.readFileSync(s.filename);
  assert.throws(()=>s.save({fullscreen:'false'}));
  assert.throws(()=>s.save({token:'please'}));
  assert.throws(()=>s.save({theme:'evil'}));
  assert.deepEqual(fs.readFileSync(s.filename),before);
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
test('corrupt data falls back safely without destructive overwrite',()=>{
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'666-buildkit-settings-'));
 try{
  const s=createStore(dir);fs.writeFileSync(s.filename,'not json','utf8');
  assert.deepEqual(s.load(),DEFAULTS);
  assert.equal(fs.readFileSync(s.filename,'utf8'),'not json');
 }finally{fs.rmSync(dir,{recursive:true,force:true})}
});
test('settings schema is closed and normalizes missing fields',()=>{
 assert.deepEqual(validate({fullscreen:false}),{fullscreen:false,language:'de',theme:'dark'});
 for(const x of [null,[],42,'x'])assert.throws(()=>validate(x));
});
