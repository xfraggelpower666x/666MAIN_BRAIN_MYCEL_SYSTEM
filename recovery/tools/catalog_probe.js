#!/usr/bin/env node
'use strict';
/** Read-only, source-hash-verified research discovery for the three recovered modules.
 *  Independent inspection tool; NOT the missing original ResearchDB runtime.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '../..');
const ORIGINALS = [
  'data/topics/topic-chaos-theory.js',
  'data/topics/topic-chaos-psytrance-psychoacoustics.js',
  'data/prompts/prompt-chaos-psytrance-suno-specialist.js'
];

function hashes() {
  const manifest = fs.readFileSync(path.join(ROOT, 'history/v1_7_1/SYSTEM_ONLY_FILE_MANIFEST_SHA256.txt'), 'utf8');
  return Object.fromEntries(manifest.trim().split(/\r?\n/).map(line => {
    const match = /^([a-f0-9]{64})  (.+)$/.exec(line);
    if (!match) throw new Error('Invalid historical SHA-256 manifest');
    return [match[2], match[1]];
  }));
}
function verifiedContent(relative, expected) {
  const p = path.join(ROOT, relative);
  const buf = fs.readFileSync(p);
  const got = crypto.createHash('sha256').update(buf).digest('hex');
  if (got !== expected) throw new Error('CHECKSUM_MISMATCH: ' + relative);
  return buf.toString('utf8');
}
function loadCatalog() {
  const expected = hashes();
  const catalog = {topics: [], prompts: []};
  const sandbox = {
    ResearchDB: Object.freeze({registerTopic: topic => catalog.topics.push(JSON.parse(JSON.stringify(topic)))}),
    PromptRegistry: Object.freeze({register: prompt => catalog.prompts.push(JSON.parse(JSON.stringify(prompt)))})
  };
  const context = vm.createContext(sandbox, {codeGeneration: {strings: false, wasm: false}});
  for (const relative of ORIGINALS) {
    if (!expected[relative]) throw new Error('NOT_IN_HISTORICAL_MANIFEST: ' + relative);
    vm.runInContext(verifiedContent(relative, expected[relative]), context, {filename: relative, timeout: 1000});
  }
  if (catalog.topics.length !== 2 || catalog.prompts.length !== 1) throw new Error('RECOVERY_REGISTRY_COUNT_CONFLICT');
  return catalog;
}
function searchCatalog(catalog, query) {
  const q = query.toLocaleLowerCase('de');
  const all = [
    ...catalog.topics.map(x => ({type: 'topic', id: x.id, title: x.title, entryCount: x.entries?.length ?? 0, ...x})),
    ...catalog.prompts.map(x => ({...x, type: 'prompt', id: x.id, title: x.title}))
  ];
  return all.filter(x => [x.id, x.title, x.description, x.category, ...(x.tags || [])]
      .filter(Boolean).some(v => String(v).toLocaleLowerCase('de').includes(q)))
    .map(x => ({type: x.type, id: x.id, title: x.title, version: x.version, entryCount: x.entryCount ?? null}));
}
function run(args) {
  const catalog = loadCatalog();
  if (!args.length || (args.length === 1 && args[0] === '--summary')) {
    return {status: 'VERIFIED_RECOVERED_CONTENT_ONLY', topics: catalog.topics.length,
      prompts: catalog.prompts.length, topicEntries: catalog.topics.reduce((n, x) => n + (x.entries?.length ?? 0), 0),
      note: 'Original v1.7.1 bootstrap remains missing; search is a separate read-only recovery tool.'};
  }
  if (args[0] === '--search' && args.length === 2 && args[1].trim()) {
    return {query: args[1], matches: searchCatalog(catalog, args[1])};
  }
  if (args[0] === '--id' && args.length === 2 && args[1].trim()) {
    const match = [...catalog.topics, ...catalog.prompts].find(x => x.id === args[1]);
    return match ? {id: match.id, title: match.title, type: catalog.topics.includes(match) ? 'topic' : 'prompt',
      version: match.version, description: match.description ?? null,
      entryCount: match.entries?.length ?? null} : {status: 'NOT_FOUND', id: args[1]};
  }
  throw new Error('Usage: node recovery/tools/catalog_probe.js [--summary | --search WORD | --id ID]');
}
if (require.main === module) {
  try {console.log(JSON.stringify(run(process.argv.slice(2)), null, 2));}
  catch (err) {console.error('BLOCKIERT: ' + err.message); process.exitCode = 2;}
}
module.exports = {loadCatalog, searchCatalog, verifiedContent, run};
