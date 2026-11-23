#!/usr/bin/env node
'use strict';
/** R01 read-only CLI. No writes, no internet, no generation claims. */
const core = require('./src/runtime.js');
function run(args) {
  const {registry, ...meta} = core.loadCatalog();
  const audit = core.report({...meta, registry});
  const [command, ...rest] = args;
  if (command === 'status' || !command) return audit;
  if (command === 'audit') return audit;
  if (command === 'menu') return {topics: registry.topics.map(t => ({id: t.id, title: t.title, entries: t.entries.length})), prompts: registry.prompts.map(p => ({id: p.id, title: p.title}))};
  if (command === 'search' && rest.length === 1) return {query: rest[0], results: core.search(registry, rest[0])};
  if (command === 'get' && rest.length === 1) return core.get(registry, rest[0]) || {status: 'NOT_FOUND', id: rest[0]};
  if (command === 'topic' && rest.length === 1) return registry.topics.find(t => t.id === rest[0]) || {status: 'NOT_FOUND', id: rest[0]};
  if (command === 'prompt' && rest.length === 1) return registry.prompts.find(p => p.id === rest[0]) || {status: 'NOT_FOUND', id: rest[0]};
  if (command === 'sources' && rest.length === 1) {
    const topic = registry.topics.find(t => t.id === rest[0]);
    return topic ? {topic: topic.id, sources: topic.sources} : {status: 'NOT_FOUND', id: rest[0]};
  }
  if (command === 'render' && rest.length >= 1) {
    const [id, ...params] = rest; const values = {};
    for (const param of params) {
      if (!param.startsWith('--var=')) throw new Error('INVALID_RENDER_FLAG');
      const raw = param.slice(6); const eq = raw.indexOf('=');
      if (eq < 1) throw new Error('INVALID_VARIABLE_ASSIGNMENT');
      const key = raw.slice(0, eq); if (Object.hasOwn(values, key)) throw new Error('DUPLICATE_VARIABLE:' + key);
      values[key] = raw.slice(eq + 1);
    }
    return core.renderPrompt(registry, id, values);
  }
  if (command === 'export' && rest.length === 1) return core.exportCatalog(registry, rest[0]);
  throw new Error('USAGE: node reimplementation/r01/cli.js [status|audit|menu|search WORD|get ID|topic ID|prompt ID|sources TOPIC_ID|render PROMPT_ID --var=key=value|export json|export md]');
}
if (require.main === module) {
  try {
    const result = run(process.argv.slice(2));
    process.stdout.write(typeof result === 'string' ? result : JSON.stringify(result, null, 2) + '\n');
    if (process.argv[2] === 'audit' && result.state !== 'VERIFIED_REIMPLEMENTATION_SUBSET') process.exitCode = 2;
  } catch (error) {
    console.error('BLOCKIERT: ' + error.message); process.exitCode = 2;
  }
}
module.exports = {run};
