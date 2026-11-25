'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {createStore,validate,DEFAULTS}=require('../r19-electron/app-settings-store.cjs');
test('buildkit defaults are fullscreen and separate from compiler',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cyber-settings-'));
  try{assert.deepEqual(createStore(dir).load(),DEFAULTS);assert.equal(fs.existsSync(path.join(dir,'settings.json')),false);}
  finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('fullscreen and language settings persist between instances',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cyber-settings-'));
  try{createStore(dir).save({fullscreen:false,language:'en',theme:'cyber'});
    assert.deepEqual(createStore(dir).load(),{fullscreen:false,language:'en',theme:'cyber'});}
  finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('unknown settings or invalid types never change stored state',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cyber-settings-'));
  try{const s=createStore(dir);s.save({fullscreen:true});const before=fs.readFileSync(s.filename);
    assert.throws(()=>s.save({fullscreen:'false'}));assert.throws(()=>s.save({token:'secret'}));
    assert.throws(()=>s.save({theme:'invalid'}));assert.deepEqual(fs.readFileSync(s.filename),before);}
  finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('corrupt settings remain untouched with safe defaults',()=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'cyber-settings-'));
  try{const s=createStore(dir);fs.writeFileSync(s.filename,'broken data');
    assert.deepEqual(s.load(),DEFAULTS);assert.equal(fs.readFileSync(s.filename,'utf8'),'broken data');}
  finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('settings validation uses closed schema',()=>{
  assert.deepEqual(validate({fullscreen:false}),{fullscreen:false,language:'de',theme:'dark'});
  for(const value of [null,[],42,'x'])assert.throws(()=>validate(value));
});
