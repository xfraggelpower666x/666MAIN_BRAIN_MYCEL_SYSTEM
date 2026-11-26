'use strict';
// Source-level IPC regression under Node, not an independent Windows Electron run.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const Module = require('node:module');
(async () => {
 const temp = fs.mkdtempSync(path.join(os.tmpdir(),'autodj-ipc-'));
 const selected = path.join(temp,'covers');fs.mkdirSync(selected);
 fs.writeFileSync(path.join(selected,'front.jpg'),Buffer.from([0xff,0xd8,0xff,0xd9]));
 const privateFolder = path.join(temp,'unselected');fs.mkdirSync(privateFolder);
 fs.writeFileSync(path.join(privateFolder,'not-selected.jpg'),Buffer.from([0xff,0xd8,0xff,0xd9]));
 const handlers = new Map();
 const electron = {
  app:{isPackaged:false,whenReady:()=>({then:cb=>{cb();}}),on:()=>{},quit:()=>{}},
  BrowserWindow:class {constructor(options){this.options=options;this.webContents={send:()=>{},setWindowOpenHandler:()=>{}};}loadFile(){}isDestroyed(){return false;}},
  dialog:{showOpenDialog:async()=>({canceled:false,filePaths:[selected]})},
  ipcMain:{handle:(name,fn)=>handlers.set(name,fn)}
 };
 const original = Module._load;
 Module._load=function(request,parent,isMain){if(request==='electron')return electron;return original.apply(this,arguments);};
 try {require('../app/main.js');}finally{Module._load=original;}
 try {
  const inspect=handlers.get('covers:inspect');assert.equal(typeof inspect,'function');
  assert.match((await inspect({},selected)).error,/selected first/);
  assert.match((await inspect({},privateFolder)).error,/selected first/);
  assert.equal(await handlers.get('folder:choose')(),selected);
  const info=await inspect({},selected);
  assert.equal(info.count,1);assert.equal(info.filename,'front.jpg');
  assert.match(info.dataUrl,/^data:image\/jpeg;base64,/);
  assert.match((await inspect({},privateFolder)).error,/selected first/);
  console.log('IPC COVER SECURITY PASS: selected-only, readonly, one preview');
 }finally{fs.rmSync(temp,{recursive:true,force:true});}
})().catch(error=>{console.error(error);process.exitCode=1;});
