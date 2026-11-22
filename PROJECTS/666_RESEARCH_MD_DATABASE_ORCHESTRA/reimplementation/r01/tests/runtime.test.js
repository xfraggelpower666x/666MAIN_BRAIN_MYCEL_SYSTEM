'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const core = require('../src/runtime.js');
const cli = require('../cli.js');
const loaded = core.loadCatalog();
const registry = loaded.registry;

test('R01 keeps its own identity and never claims historical rehydration', () => {
  const report = core.report(loaded);
  assert.equal(report.implementation, '0.1.0-reimpl-r01');
  assert.equal(report.historicalOriginalsRehydrated, false);
  assert.equal(report.historicalManifestFiles, 136);
  assert.equal(report.originalFilesVerified, 3);
  assert.equal(report.state, 'VERIFIED_REIMPLEMENTATION_SUBSET');
});
test('two topics / 28 entries / one prompt / 25 sources verified', () => {
  const report = core.report(loaded);
  assert.deepEqual([report.topics, report.entries, report.prompts, report.sources], [2, 28, 1, 25]);
  assert.deepEqual(report.issues, []);
});
test('both recovered topic IDs are stable', () => {
  assert.deepEqual(registry.topics.map(x => x.id), ['chaos-theory', 'chaos-psytrance-psychoacoustics']);
});
test('menu keeps topic and prompt namespaces separate', () => {
  const result = cli.run(['menu']);
  assert.equal(result.topics.length, 2);
  assert.equal(result.prompts.length, 1);
});
test('term search looks through content entries, not only topic titles', () => {
  const result = core.search(registry, 'Lyapunov');
  assert.ok(result.some(x => x.type === 'entry' && x.id.startsWith('chaos-')));
});
test('psycho search resolves topic and prompt', () => {
  const result = core.search(registry, 'psycho');
  assert.ok(result.some(x => x.type === 'topic'));
  assert.ok(result.some(x => x.type === 'prompt'));
});
test('search returns empty but valid array when no match', () => {
  assert.deepEqual(core.search(registry, 'qzxUNLIKELY9999'), []);
});
test('search blocks invalid values and limit', () => {
  for (const q of ['', '  ', ' '.repeat(201), null]) assert.throws(() => core.search(registry, q));
  assert.throws(() => core.search(registry, 'psycho', 100000));
});
test('source references resolve and no cross-link errors', () => {
  const r = core.validateRegistry(registry);
  assert.equal(r.sourceCount, 25);
  assert.deepEqual(r.issues, []);
});
test('broken source references show a specific audit issue', () => {
  const other = structuredClone(registry);
  other.topics[0].entries[0].sourceIds.push('unknown-source');
  assert.match(core.validateRegistry(other).issues.join('|'), /UNRESOLVED_CITATION/);
});
test('duplicate entry IDs cause audit failure', () => {
  const other = structuredClone(registry);
  other.topics[0].entries.push(structuredClone(other.topics[0].entries[0]));
  assert.match(core.validateRegistry(other).issues.join('|'), /DUPLICATE_ENTRY/);
});
test('missing or modified verified source blocks before evaluation', () => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'ro-r01-'));
  try {
    fs.mkdirSync(path.join(temp, 'history/v1_7_1'), {recursive: true});
    fs.mkdirSync(path.join(temp, 'data/topics'), {recursive: true});
    fs.mkdirSync(path.join(temp, 'data/prompts'), {recursive: true});
    fs.copyFileSync(path.join(core.ROOT, core.HISTORIC_MANIFEST), path.join(temp, core.HISTORIC_MANIFEST));
    for (const rel of core.ORIGINAL_MODULES) {
      fs.copyFileSync(path.join(core.ROOT, rel), path.join(temp, rel));
    }
    const target = path.join(temp, core.ORIGINAL_MODULES[0]);
    fs.appendFileSync(target, '\n// altered');
    assert.throws(() => core.loadCatalog(temp), /CHECKSUM_MISMATCH/);
    fs.unlinkSync(target);
    assert.throws(() => core.loadCatalog(temp), /ENOENT/);
  } finally { fs.rmSync(temp, {recursive: true, force: true}); }
});
test('exact prompt ID finds one source prompt', () => {
  const p = core.get(registry, 'chaos-psytrance-suno-prompt-specialist');
  assert.equal(p.type, 'prompt');
});
test('render uses only declared variables, with defaults', () => {
  const out = core.renderPrompt(registry, 'chaos-psytrance-suno-prompt-specialist', {bpm: '148', concept: 'bounded groove'});
  assert.ok(out.rendered.includes('148'));
  assert.ok(out.rendered.includes('bounded groove'));
  assert.equal(out.rendered.includes('$' + '{'), false);
});
test('render rejects unknown variables and control characters', () => {
  const id = 'chaos-psytrance-suno-prompt-specialist';
  assert.throws(() => core.renderPrompt(registry, id, {unknown: 'test'}), /UNKNOWN_VARIABLE/);
  assert.throws(() => core.renderPrompt(registry, id, {bpm: '\nfoo'}), /INVALID_VARIABLE_VALUE/);
  assert.throws(() => core.renderPrompt(registry, id, {concept: 'x'.repeat(201)}), /INVALID_VARIABLE_VALUE/);
});
test('CLI rejects duplicate or unsupported render assignments', () => {
  const id = 'chaos-psytrance-suno-prompt-specialist';
  assert.throws(() => cli.run(['render', id, '--var=bpm=140', '--var=bpm=148']), /DUPLICATE_VARIABLE/);
  assert.throws(() => cli.run(['render', id, '--bad']), /INVALID_RENDER_FLAG/);
});
test('JSON export is parseable and scope-labeled', () => {
  const obj = JSON.parse(core.exportCatalog(registry, 'json'));
  assert.equal(obj.scope, 'RECOVERED_ORIGINAL_SUBSET');
  assert.equal(obj.topics.length, 2);
  assert.equal(obj.prompts.length, 1);
});
test('Markdown export includes source provenance but no claims of full recovery', () => {
  const md = core.exportCatalog(registry, 'md');
  assert.ok(md.includes('Sources'));
  assert.ok(md.includes('Not the complete historical system'));
});
test('invalid format or command fails closed', () => {
  assert.throws(() => core.exportCatalog(registry, 'pdf'), /UNKNOWN_EXPORT_FORMAT/);
  assert.throws(() => cli.run(['delete', 'everything']), /USAGE/);
});
test('R01 module performs no file writes', () => {
  const runtime = fs.readFileSync(path.join(__dirname, '../src/runtime.js'), 'utf8');
  const entry = fs.readFileSync(path.join(__dirname, '../cli.js'), 'utf8');
  for (const text of [runtime, entry]) {
    assert.doesNotMatch(text, /writeFileSync|appendFileSync|rmSync|unlinkSync|execSync|spawnSync|fetch\(/);
  }
});
