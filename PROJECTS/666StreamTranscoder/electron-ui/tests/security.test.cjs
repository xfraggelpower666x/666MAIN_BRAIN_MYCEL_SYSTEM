'use strict';
// Offline source-scope tests. No Electron module or Windows device required.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = (name) => fs.readFileSync(path.join(root, name), 'utf8');

test('renderer is isolated from Node and main uses sandbox', () => {
  const main = read('main.cjs');
  assert.match(main, /contextIsolation:\s*true/);
  assert.match(main, /sandbox:\s*true/);
  assert.match(main, /nodeIntegration:\s*false/);
  assert.match(main, /webSecurity:\s*true/);
  assert.match(main, /setWindowOpenHandler/);
  assert.match(main, /will-navigate/);
  assert.doesNotMatch(main, /child_process|spawn\s*\(|execFile\s*\(/);
});

test('preload exposes only disconnected read-only feature flags', () => {
  const preload = read('preload.cjs');
  assert.match(preload, /DISCONNECTED_PREVIEW/);
  for (const value of ['engineConnected', 'canBroadcast', 'canMonitor', 'canChangeSettings']) {
    assert.match(preload, new RegExp(value + ':\\s*false'));
  }
  assert.match(preload, /ipcRenderer\.invoke\('stream:status'\)/);
  assert.doesNotMatch(preload, /execFile|spawn|stream:command/);
});

test('all broadcast-affecting controls are disabled', () => {
  const html = read('index.html');
  assert.match(html, /GO LIVE[^<]*<\/button>/);
  assert.match(html, /SKIP[^<]*<\/button>/);
  assert.match(html, /<button disabled>GO LIVE/);
  assert.match(html, /<button disabled>SKIP/);
  assert.match(html, /Keine Telemetrie/);
  assert.match(html, /Content-Security-Policy/);
  assert.doesNotMatch(html, /https?:\/\//);
});

test('renderer changes presentation only', () => {
  const renderer = read('renderer.js');
  assert.match(renderer, /dataset\.view/);
  assert.doesNotMatch(renderer, /fetch\s*\(|ipcRenderer|child_process/);
});

test('the UI package does not claim to package the 3DX audio runtime', () => {
  const pkg = JSON.parse(read('package.json'));
  assert.equal(pkg.private, true);
  assert.equal(pkg.main, 'main.cjs');
  assert.equal(typeof pkg.scripts.start, 'string');
  assert.equal(typeof pkg.scripts.check, 'string');
  assert.equal(typeof pkg.scripts.test, 'string');
  // A preview-only package is allowed, but it must NEVER claim audio integration.
  assert.equal(pkg.build.productName, '666StreamTranscoder UI PREVIEW');
  assert.equal(pkg.build.directories.output, 'dist-preview');
  assert.ok(pkg.build.files.includes('status-contract.cjs'));
  for (const forbidden of ['radiostreamer/**/*','../radiostreamer/**/*','ffmpeg.exe','RadioStreamer.py']) {
    assert.ok(!pkg.build.files.includes(forbidden), 'Unexpected audio asset: ' + forbidden);
  }
  assert.match(pkg.scripts['build:windows-preview'], /electron-builder/);
});


test('local status rejects malformed, stale and injected payloads', () => {
  const {validateStatus} = require('../status-contract.cjs');
  const now = 1000000;
  const components = Object.fromEntries(['source','monitor','encoder','server','relay','error'].map(k => [k,'off']));
  const good = {schema:'666.streamtranscoder.desktop-status.v1',timestamp_ms:now,
    pid:123,status:'off',on_air:false,monitor_active:false,input_dbfs:null,
    output_dbfs:-15,components};
  assert.ok(validateStatus(good,now));
  assert.equal(validateStatus({...good,timestamp_ms:now-6000},now),null);
  assert.equal(validateStatus({...good,input_dbfs:Infinity},now),null);
  assert.equal(validateStatus({...good,components:{...components,source:'<script>'}},now),null);
  assert.equal(validateStatus({...good,on_air:true},now),null);
  assert.equal(validateStatus({...good,providerPassword:'secret'},now).providerPassword,undefined);
});
