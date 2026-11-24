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
  assert.doesNotMatch(preload, /ipcRenderer|execFile|spawn/);
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
  assert.equal(pkg.build, undefined);
});
