'use strict';
/**
 * REIMPLEMENTATION R01 — separate read-only research registry, NOT the original 1.7.1 runtime.
 * Loads exactly three historically SHA-256 verified source modules. No repository writes.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '../../..');
const HISTORIC_MANIFEST = 'history/v1_7_1/SYSTEM_ONLY_FILE_MANIFEST_SHA256.txt';
const ORIGINAL_MODULES = Object.freeze([
  'data/topics/topic-chaos-theory.js',
  'data/topics/topic-chaos-psytrance-psychoacoustics.js',
  'data/prompts/prompt-chaos-psytrance-suno-specialist.js'
]);
const VERSION = '0.1.0-reimpl-r01';
const CONFIRMED_STATES = new Set(['confirmed', 'partial', 'needs_review', 'contradicted', 'historical', 'quarantined']);

function invariant(condition, message) {
  if (!condition) throw new Error(message);
}
function manifest(root = ROOT) {
  const content = fs.readFileSync(path.join(root, HISTORIC_MANIFEST), 'utf8');
  const result = new Map();
  for (const [index, line] of content.split(/\r?\n/).entries()) {
    if (!line.trim()) continue;
    const match = /^([0-9a-fA-F]{64})  (.+)$/.exec(line);
    invariant(match, 'INVALID_MANIFEST_LINE:' + (index + 1));
    invariant(!result.has(match[2]), 'DUPLICATE_MANIFEST_PATH:' + match[2]);
    result.set(match[2], match[1].toLowerCase());
  }
  return result;
}
function verifyFile(root, relative, expected) {
  invariant(expected, 'UNLISTED_SOURCE:' + relative);
  const full = path.join(root, relative);
  const bytes = fs.readFileSync(full);
  const actual = crypto.createHash('sha256').update(bytes).digest('hex');
  invariant(actual === expected, 'CHECKSUM_MISMATCH:' + relative);
  return bytes.toString('utf8');
}
function text(value, name, max = 10000) {
  invariant(typeof value === 'string' && value.trim().length > 0 && value.length <= max, 'INVALID_' + name);
  return value;
}
function validateRegistry(registry) {
  const issues = [];
  const keys = new Set();
  const sources = new Map();
  for (const topic of registry.topics) {
    if (!topic || typeof topic !== 'object' || !topic.id || !topic.title || !Array.isArray(topic.entries) || !Array.isArray(topic.sources)) {
      issues.push('INVALID_TOPIC_SCHEMA:' + (topic?.id ?? '?')); continue;
    }
    const key = 'topic:' + topic.id;
    if (keys.has(key)) issues.push('DUPLICATE_TOPIC:' + topic.id);
    keys.add(key);
    const localEntries = new Set();
    const localSources = new Set();
    for (const entry of topic.entries) {
      if (typeof entry?.id !== 'string' || typeof entry?.summary !== 'string') issues.push('INVALID_ENTRY:' + topic.id);
      if (localEntries.has(entry.id)) issues.push('DUPLICATE_ENTRY:' + entry.id);
      localEntries.add(entry.id);
      if (!CONFIRMED_STATES.has(entry.status)) issues.push('UNRECOGNIZED_STATUS:' + entry.id);
    }
    for (const source of topic.sources) {
      if (!source?.id || !source?.title) issues.push('INVALID_SOURCE:' + topic.id);
      if (localSources.has(source.id)) issues.push('DUPLICATE_SOURCE:' + source.id);
      localSources.add(source.id);
      sources.set(topic.id + ':' + source.id, source);
      for (const entryId of source.usedFor ?? []) {
        if (!localEntries.has(entryId)) issues.push('BROKEN_SOURCE_USED_FOR:' + source.id + ':' + entryId);
      }
    }
    for (const entry of topic.entries) {
      for (const sourceId of entry.sourceIds ?? []) {
        if (!localSources.has(sourceId)) issues.push('UNRESOLVED_CITATION:' + entry.id + ':' + sourceId);
      }
    }
  }
  for (const prompt of registry.prompts) {
    if (typeof prompt?.id !== 'string' || !Array.isArray(prompt.variables) || typeof prompt.content !== 'string') {
      issues.push('INVALID_PROMPT_SCHEMA:' + (prompt?.id ?? '?')); continue;
    }
    if (keys.has('prompt:' + prompt.id)) issues.push('DUPLICATE_PROMPT:' + prompt.id);
    keys.add('prompt:' + prompt.id);
  }
  return {issues, sourceCount: sources.size};
}
function loadCatalog(root = ROOT) {
  const expected = manifest(root);
  const registry = {topics: [], prompts: []};
  const scope = {
    ResearchDB: Object.freeze({registerTopic(value) {registry.topics.push(JSON.parse(JSON.stringify(value)));}}),
    PromptRegistry: Object.freeze({register(value) {registry.prompts.push(JSON.parse(JSON.stringify(value)));}})
  };
  const ctx = vm.createContext(scope, {codeGeneration: {strings: false, wasm: false}});
  for (const relative of ORIGINAL_MODULES) {
    const source = verifyFile(root, relative, expected.get(relative));
    vm.runInContext(source, ctx, {filename: relative, timeout: 1000});
  }
  invariant(registry.topics.length === 2 && registry.prompts.length === 1, 'UNEXPECTED_MODULE_COUNT');
  const result = validateRegistry(registry);
  return {registry, validation: result, originalCount: ORIGINAL_MODULES.length, expectedCount: expected.size};
}
function items(registry) {
  const list = [];
  for (const topic of registry.topics) {
    list.push({type: 'topic', id: topic.id, title: topic.title, summary: topic.description || '', topicId: topic.id});
    for (const entry of topic.entries) list.push({type: 'entry', id: entry.id, title: entry.title, summary: entry.summary || '', details: entry.details || '', tags: entry.tags || [], topicId: topic.id, status: entry.status, sourceIds: entry.sourceIds || []});
    for (const source of topic.sources) list.push({type: 'source', id: source.id, title: source.title, summary: source.notes || '', topicId: topic.id, url: source.url || '', trustLevel: source.trustLevel || null});
  }
  for (const prompt of registry.prompts) list.push({type: 'prompt', id: prompt.id, title: prompt.title, summary: prompt.description || '', tags: prompt.tags || []});
  return list;
}
function search(registry, query, limit = 100) {
  text(query, 'QUERY', 200);
  invariant(Number.isInteger(limit) && limit >= 1 && limit <= 100, 'INVALID_LIMIT');
  const words = query.trim().toLocaleLowerCase('de').split(/\s+/).filter(Boolean);
  const scored = items(registry).map(item => {
    const title = String(item.title || '').toLocaleLowerCase('de');
    const body = [item.id, item.summary, item.details, ...(item.tags || [])].join(' ').toLocaleLowerCase('de');
    const matches = words.every(word => title.includes(word) || body.includes(word));
    const score = words.reduce((n, word) => n + (title.includes(word) ? 4 : 0) + (body.includes(word) ? 1 : 0), 0);
    return {item, score, matches};
  }).filter(x => x.matches).sort((a, b) => b.score - a.score || a.item.id.localeCompare(b.item.id));
  return scored.slice(0, limit).map(({item, score}) => ({...item, score}));
}
function get(registry, id, kind = null) {
  text(id, 'ID', 200);
  const matches = items(registry).filter(x => x.id === id && (kind === null || kind === x.type));
  invariant(matches.length <= 1, 'AMBIGUOUS_ID:' + id);
  return matches[0] ?? null;
}
function renderPrompt(registry, promptId, values = {}) {
  text(promptId, 'PROMPT_ID', 200);
  invariant(values && !Array.isArray(values) && typeof values === 'object', 'INVALID_VARIABLE_MAP');
  const prompt = registry.prompts.find(x => x.id === promptId);
  invariant(prompt, 'PROMPT_NOT_FOUND:' + promptId);
  for (const [key, value] of Object.entries(values)) {
    invariant(prompt.variables.includes(key), 'UNKNOWN_VARIABLE:' + key);
    invariant(typeof value === 'string' && value.length <= 200 && !/[\u0000-\u001f]/.test(value), 'INVALID_VARIABLE_VALUE:' + key);
  }
  const result = prompt.content.replace(/\$\{([a-z][a-z0-9_]*):([^}]*)\}/g, (_, key, fallback) => {
    invariant(prompt.variables.includes(key), 'UNDECLARED_TEMPLATE_VARIABLE:' + key);
    return Object.hasOwn(values, key) ? values[key] : fallback;
  });
  invariant(!/\$\{[^}]*\}/.test(result), 'UNRESOLVED_TEMPLATE_VARIABLE');
  return {id: prompt.id, version: prompt.version, rendered: result, variablesApplied: Object.keys(values)};
}
function report(loaded) {
  const {registry, validation, originalCount, expectedCount} = loaded;
  const entries = registry.topics.reduce((n, t) => n + t.entries.length, 0);
  return {implementation: VERSION, scope: 'SEPARATE_RECOVERY_REIMPLEMENTATION', state: validation.issues.length ? 'NEEDS_REVISION' : 'VERIFIED_REIMPLEMENTATION_SUBSET',
    historicalOriginalsRehydrated: false, originalFilesVerified: originalCount, historicalManifestFiles: expectedCount,
    topics: registry.topics.length, entries, prompts: registry.prompts.length, sources: validation.sourceCount,
    issues: validation.issues, note: 'Subset validation is not a full v1.7.1 source readback or historical freeze.'};
}
function exportCatalog(registry, format = 'json') {
  invariant(['json', 'md'].includes(format), 'UNKNOWN_EXPORT_FORMAT');
  if (format === 'json') return JSON.stringify({implementation: VERSION, scope: 'RECOVERED_ORIGINAL_SUBSET', topics: registry.topics, prompts: registry.prompts}, null, 2) + '\n';
  const out = ['# RESEARCH ORCHESTRA — recovered-source export', '', 'Scope: three SHA-256 verified originals; independent R01 runtime. Not the complete historical system.', ''];
  for (const topic of registry.topics) {
    out.push('## ' + topic.title, '', topic.description || '', '');
    for (const entry of topic.entries) {
      out.push('### ' + entry.title, '', 'ID: ' + entry.id + ' · Status: ' + entry.status, '', entry.summary || '', '', entry.details || '', '', 'Source IDs: ' + (entry.sourceIds || []).join(', '), '');
    }
    out.push('### Sources', '');
    for (const s of topic.sources) out.push('- ' + s.title + ' (' + s.id + '): ' + (s.url || 'no URL'));
    out.push('');
  }
  out.push('## Prompt modules', '');
  for (const p of registry.prompts) out.push('- ' + p.title + ' (' + p.id + ')');
  return out.join('\n') + '\n';
}
module.exports = {VERSION, ROOT, ORIGINAL_MODULES, HISTORIC_MANIFEST, manifest, verifyFile, validateRegistry, loadCatalog, items, search, get, renderPrompt, report, exportCatalog};
