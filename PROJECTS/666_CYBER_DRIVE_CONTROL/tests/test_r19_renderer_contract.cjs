'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'..','r19-electron','renderer.js'),'utf8');
const start=code.indexOf('function bindingActive(');
const end=code.indexOf('\nfunction drawD(',start);
assert.ok(start>=0&&end>start,'bindingActive must remain available in renderer');
const fn=vm.runInNewContext(code.slice(start,end)+'\nbindingActive');
test('per-binding thresholds control preview, not global settings',()=>{
  const rate={read_bps:8192,write_bps:0};
  assert.equal(fn({mode:'read',threshold_kib:4},rate),true);
  assert.equal(fn({mode:'read',threshold_kib:16},rate),false);
  assert.equal(fn({mode:'write',threshold_kib:4},rate),false);
});
test('unavailable or invalid rates do not falsely activate LEDs',()=>{
  assert.equal(fn({mode:'read',threshold_kib:4},undefined),false);
  assert.equal(fn({mode:'either',threshold_kib:4},{read_bps:null,write_bps:null}),false);
  assert.equal(fn({mode:'either',threshold_kib:4},{read_bps:Infinity,write_bps:0}),false);
  assert.equal(fn({mode:'off',threshold_kib:0},{read_bps:999999,write_bps:999999}),false);
});
test('read and write remain independent',()=>{
  const rate={read_bps:0,write_bps:7000};
  assert.equal(fn({mode:'either',threshold_kib:4},rate),true);
  assert.equal(fn({mode:'write',threshold_kib:4},rate),true);
  assert.equal(fn({mode:'read',threshold_kib:4},rate),false);
});
