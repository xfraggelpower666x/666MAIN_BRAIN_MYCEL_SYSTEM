"use strict";
const assert = require('node:assert/strict');
const test = require('node:test');
const { trustedMainFrame, assertTrustedMainFrame } = require('../electron/ipc-guards.cjs');
const frame={};
const contents={mainFrame:frame};
const win={isDestroyed:()=>false,webContents:contents};
test('authorized original main frame is accepted',()=>{
  assert.equal(trustedMainFrame({sender:contents,senderFrame:frame},win),true);
  assert.doesNotThrow(()=>assertTrustedMainFrame({sender:contents,senderFrame:frame},win));
});
test('foreign, child, destroyed or absent window IPC is rejected',()=>{
  for(const event of [{sender:{},senderFrame:frame},{sender:contents,senderFrame:{}},{sender:contents},null]){
    assert.equal(trustedMainFrame(event,win),false);
    assert.throws(()=>assertTrustedMainFrame(event,win),/Unauthorized/);
  }
  assert.equal(trustedMainFrame({sender:contents,senderFrame:frame},null),false);
  assert.equal(trustedMainFrame({sender:contents,senderFrame:frame},{...win,isDestroyed:()=>true}),false);
});
