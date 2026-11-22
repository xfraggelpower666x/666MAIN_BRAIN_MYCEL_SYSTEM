'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const probe = require('../tools/catalog_probe.js');

test('three SHA-256 verified original modules load without original runtime', () => {
  const loaded = probe.loadCatalog();
  assert.equal(loaded.topics.length, 2);
  assert.equal(loaded.prompts.length, 1);
});
test('read-only catalog summary is correctly labeled', () => {
  const out = probe.run(['--summary']);
  assert.equal(out.status, 'VERIFIED_RECOVERED_CONTENT_ONLY');
  assert.ok(out.topicEntries > 0);
});
test('search finds psychoacoustic research source', () => {
  const found = probe.run(['--search', 'psycho']);
  assert.ok(found.matches.length >= 1);
  assert.ok(found.matches.every(x => x.id && x.title));
  assert.ok(found.matches.some(x => x.type === 'prompt'));
});
test('unknown flags fail closed', () => {
  assert.throws(() => probe.run(['--execute', '/tmp/x']));
});
test('content hash mutation is blocked before evaluation', () => {
  assert.throws(() => probe.verifiedContent('data/topics/topic-chaos-theory.js', '0'.repeat(64)), /CHECKSUM_MISMATCH/);
});
