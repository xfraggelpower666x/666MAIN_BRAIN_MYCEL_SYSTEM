#!/usr/bin/env node
'use strict';
const {boot} = require('./src/bootstrap.js');
function run(argv) {
  const runtime = boot();
  const [cmd, ...rest] = argv;
  if (!cmd || cmd === 'status') {
    return {identity: runtime.identity, version: runtime.version, release: runtime.release,
      production: runtime.production, historicalReadback: runtime.historicalReadback,
      research: {topics: runtime.report.topics, entries: runtime.report.entries, sources: runtime.report.sources, prompts: runtime.report.prompts},
      blindAB: 'in-memory-only; anonymized media must be supplied separately'};
  }
  if (cmd === 'search' && rest.length === 1) return {query: rest[0], matches: runtime.search(rest[0])};
  if (cmd === 'get' && rest.length === 1) return runtime.get(rest[0]);
  throw new Error('USAGE: node reimplementation/r02/cli.js [status|search WORD|get ID]');
}
if (require.main === module) {
  try { process.stdout.write(JSON.stringify(run(process.argv.slice(2)), null, 2) + '\n'); }
  catch (error) { console.error('BLOCKIERT: ' + error.message); process.exitCode = 2; }
}
module.exports = {run};
