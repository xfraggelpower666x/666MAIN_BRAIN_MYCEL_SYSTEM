const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const p = process.argv[2];
const code = fs.readFileSync(p, 'utf8').replace('await mainMenu();\nScript.complete();', '');
let files, clipboard, route, webviews, checks = 0;
const bump = () => { checks += 1; };
const io = {
  documentsDirectory: () => '/icloud', joinPath: (a,b) => a+'/'+b,
  fileExists: (p) => files.has(p), createDirectory: (p) => files.set(p, ''),
  writeString: (p,d) => files.set(p,d), readString: (p) => files.get(p),
  fileSize: (p) => Buffer.byteLength(files.get(p)), remove: (p) => files.delete(p)
};
const ssr = '<html><head><title>SSR</title></head><body><ol data-conversation-transcript><li id="a" data-message-role="assistant"><div data-assistant-markdown-root>Hello SSR<img src="https://example.invalid/a.png"></div></li></ol>'+' '.repeat(550)+'</body></html>';
class Alert {
  addAction() {}
  addCancelAction() {}
  presentAlert() { return Promise.resolve(0); }
}
class Request {
  loadString() {
    if (route === 'network-fail') throw new Error('fixture network unavailable');
    return route === 'direct' ? ssr : '<html><body>'+ ' '.repeat(550)+'</body></html>';
  }
}
class WebView {
  loadHTML() { this.kind = 'source'; webviews.push('source'); }
  loadRequest() { this.kind = 'live'; webviews.push('live'); }
  evaluateJavaScript(script) {
    new vm.Script(script);
    if (route === 'failed' || (this.kind === 'source' && route === 'live'))
      return {items:[], diagnostics:{readyState:'complete'}};
    return {items:[{role:'assistant',text:'Recovered '+this.kind,id:'a'}],title:'Fixture'};
  }
}
async function scenario(mode, expected, parser, want) {
  route = mode; files = new Map(); webviews = []; clipboard = '';
  const ctx = vm.createContext({ FileManager:{iCloud:()=>io}, Alert, Request, WebView,
    Timer:{schedule:(_,__,cb)=>cb()}, console:{log(){}},
    Pasteboard:{copyString:x=>{clipboard=x;},pasteString:()=>''} });
  await vm.runInContext('(async()=>{'+code+
    '\nresolveShareUrl = async () => "https://chatgpt.com/share/fixture";'+
    '\nawait runHostAcceptance();'+
    '\n})();', ctx);
  const receipt = JSON.parse(clipboard);
  assert.equal(receipt.version,'1.0.9');
  assert.equal(receipt.status, expected ? 'HOST_ACCEPTANCE_PASS' : 'HOST_ACCEPTANCE_FAIL');
  assert.deepEqual(webviews,want);
  assert.equal(receipt.importPath,expected);
  assert.equal(receipt.parser,parser);
  assert.equal(receipt.importAttempts.length, mode === 'direct' ? 1 : mode === 'source' ? 2 : 3);
  const readback = [...files.entries()].find(([p])=>p.endsWith('/host_acceptance_receipt.json'));
  assert.equal(readback[1],clipboard);
  if (expected) {
    assert.equal(receipt.messageCount,1);
    assert.ok(receipt.checks.every(item=>item.status==='PASS'));
    const exported = [...files.entries()].find(([p])=>p.endsWith('/chat.json'));
    assert.equal(JSON.parse(exported[1]).messages[0].id,'a');
  } else assert.ok(receipt.error.includes('LIVE_WEBVIEW'));
  bump();

}
(async()=>{
  await scenario('direct','DIRECT_SOURCE','ssr-source-transcript',[]);
  await scenario('source','SOURCE_DOM','source-dom-fallback',['source']);
  await scenario('live','LIVE_WEBVIEW','dom-fallback',['source','live']);
  await scenario('network-fail','LIVE_WEBVIEW','dom-fallback',['live']);
  await scenario('failed',undefined,null,['source','live']);
  route='direct'; clipboard='';
  await vm.runInContext('(async()=>{'+code+'\nawait runOfflineSelfTest();})();',vm.createContext({
    FileManager:{iCloud:()=>io}, Alert, WebView, Script:{}, Pasteboard:{copyString:x=>{clipboard=x;}}
  }));
  const self = JSON.parse(clipboard);
  assert.equal(self.status,'SELFTEST_PASS'); assert.equal(self.passed,7);
  bump();
  console.log(`NODE_VM ${checks}/6 PASS · Scriptable-APIs per Testdouble`);
})().catch(e=>{console.error(e);process.exitCode=1;});
