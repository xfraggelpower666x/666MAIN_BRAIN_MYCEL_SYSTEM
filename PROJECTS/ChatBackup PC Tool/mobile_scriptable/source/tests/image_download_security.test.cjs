// Standalone Node test of Scriptable URL and image-fetch boundary (no device, no network).
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.resolve(__dirname, '../666_CHATBACKUP_SCRIPTABLE_IPHONE_v1.0.9.js'), 'utf8');
const start = source.indexOf('// Safety boundary for image URLs');
const end = source.indexOf('async function imageAction(asset, i)', start);
assert.ok(start >= 0 && end > start, 'security boundary missing');
const mock = { data: {length:12}, calls:[], response:{headers:{"Content-Length":"12"}} };
class Request {
  constructor(url){this.url=url;this.response=mock.response;mock.calls.push(url);}
  async load(){return mock.data;}
}
const context = vm.createContext({Request, CONFIG:{REQUEST_TIMEOUT_SECONDS:5}, Error});
vm.runInContext(source.slice(start,end), context);
const valid = vm.runInContext('isSafeRemoteImageUrl', context);
const fetch = vm.runInContext('fetchSafeImageBytes', context);
for (const url of [
  'http://cdn.example.com/a.png',
  'https://127.0.0.1/a.png',
  'https://[::1]/image.png',
  'https://localhost/image.png',
  'https://cdn.local/a.png',
  'https://user@cdn.example.com/a.png',
  'https://cdn.example.com:8080/a.png',
  'https://cdn.example.com/#frag',
  'https://cdn.example.com/\nimage.png',
]) assert.equal(valid(url), false, 'not blocked: '+JSON.stringify(url));
assert.equal(valid('https://files.oaiusercontent.com/file.png?sig=abc'), true);
(async()=>{
  assert.equal((await fetch('https://files.oaiusercontent.com/a.png')).length, 12);
  const before = mock.calls.length;
  await assert.rejects(fetch('http://127.0.0.1/'), /Blocked unsafe image URL/);
  assert.equal(mock.calls.length, before, 'unsafe URL contacted');
  mock.data = {length:30*1024*1024+1};mock.response={headers:{}};
  await assert.rejects(fetch('https://cdn.example.com/a.png'), /30 MB/);
  console.log('SCRIPTABLE_IMAGE_SECURITY 11/11 PASS - offline mocks');
})().catch(e=>{console.error(e);process.exitCode=1;});
