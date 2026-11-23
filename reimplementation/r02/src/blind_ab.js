'use strict';
/**
 * R02: isolated in-memory blind A/B protocol. NEW implementation, not historical code.
 * All functions are pure except cryptographic ID generation and timestamps.
 * Scores and operator manifests are never persisted or published automatically.
 */
const crypto = require('node:crypto');
const SESSION_SCHEMA = 'research-orchestra/blind-ab/r02-v1';
const ID = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$/;
const BAD = (code) => { throw new Error(code); };
const assert = (truth, code) => { if (!truth) BAD(code); };
const plain = (o) => o !== null && typeof o === 'object' && !Array.isArray(o) && (Object.getPrototypeOf(o) === Object.prototype || Object.getPrototypeOf(o) === null);
const keys = (o, allowed, required = allowed) => {
  assert(plain(o), 'INVALID_OBJECT');
  assert(Object.keys(o).every(k => allowed.includes(k)), 'UNKNOWN_FIELD');
  assert(required.every(k => Object.hasOwn(o, k)), 'MISSING_FIELD');
};
const unique = (xs) => new Set(xs).size === xs.length;
const validId = (s) => typeof s === 'string' && ID.test(s);
const validDate = (s) => typeof s === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$/.test(s) && Number.isFinite(Date.parse(s));
const checkList = (list, min, max, label) => assert(Array.isArray(list) && list.length >= min && list.length <= max, 'INVALID_' + label + '_COUNT');

function validate(session) {
  keys(session, ['schema', 'id', 'phase', 'createdAt', 'lockedAt', 'criteria', 'evaluators', 'mapping', 'ratings']);
  assert(session.schema === SESSION_SCHEMA, 'INVALID_SESSION_SCHEMA');
  assert(validId(session.id), 'INVALID_SESSION_ID');
  assert(['EVALUATING', 'LOCKED'].includes(session.phase), 'INVALID_PHASE');
  assert(validDate(session.createdAt), 'INVALID_CREATED_AT');
  assert(session.phase === 'LOCKED' ? validDate(session.lockedAt) : session.lockedAt === null, 'INVALID_LOCK_STATE');
  checkList(session.criteria, 1, 12, 'CRITERIA');
  assert(session.criteria.every(validId) && unique(session.criteria), 'INVALID_CRITERIA');
  checkList(session.evaluators, 1, 20, 'EVALUATOR');
  assert(session.evaluators.every(validId) && unique(session.evaluators), 'INVALID_EVALUATORS');
  checkList(session.mapping, 2, 12, 'VARIANT');
  const blinded = [], originals = [];
  for (const pair of session.mapping) {
    keys(pair, ['blindId', 'sourceId', 'operatorRef']);
    assert(validId(pair.blindId) && validId(pair.sourceId), 'INVALID_MAPPING_ID');
    assert(typeof pair.operatorRef === 'string' && pair.operatorRef.length <= 250 && !/[\x00-\x1f]/.test(pair.operatorRef), 'INVALID_OPERATOR_REF');
    blinded.push(pair.blindId); originals.push(pair.sourceId);
  }
  assert(unique(blinded) && unique(originals), 'DUPLICATE_MAPPING');
  assert(Array.isArray(session.ratings) && session.ratings.length <= session.evaluators.length * session.mapping.length, 'INVALID_RATINGS');
  const seen = new Set();
  for (const rating of session.ratings) {
    keys(rating, ['evaluatorId', 'blindId', 'scores']);
    assert(session.evaluators.includes(rating.evaluatorId) && blinded.includes(rating.blindId), 'UNREGISTERED_RATING');
    const pair = rating.evaluatorId + '\0' + rating.blindId;
    assert(!seen.has(pair), 'DUPLICATE_RATING'); seen.add(pair);
    assert(plain(rating.scores), 'INVALID_SCORES');
    assert(Object.keys(rating.scores).length === session.criteria.length && session.criteria.every(k => Object.hasOwn(rating.scores, k)), 'INCOMPLETE_CRITERIA');
    for (const value of Object.values(rating.scores)) assert(typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 100, 'INVALID_SCORE');
  }
  if (session.phase === 'LOCKED') assert(seen.size === session.evaluators.length * session.mapping.length, 'LOCKED_WITH_MISSING_RATINGS');
  return session;
}
function createSession(config) {
  keys(config, ['id', 'candidates', 'evaluators', 'criteria']);
  assert(validId(config.id), 'INVALID_SESSION_ID');
  checkList(config.candidates, 2, 12, 'VARIANT');
  const ids = [];
  for (const candidate of config.candidates) {
    keys(candidate, ['id', 'operatorRef'], ['id']);
    assert(validId(candidate.id), 'INVALID_CANDIDATE_ID');
    ids.push(candidate.id);
  }
  assert(unique(ids), 'DUPLICATE_CANDIDATE');
  // Fisher–Yates uses crypto RNG rather than predictable shuffle.
  const candidates = config.candidates.map(x => ({...x}));
  for (let i = candidates.length - 1; i > 0; i--) {
    const j = crypto.randomInt(i + 1); [candidates[i], candidates[j]] = [candidates[j], candidates[i]];
  }
  const mapping = candidates.map(x => ({blindId: 'B-' + crypto.randomUUID(), sourceId: x.id, operatorRef: x.operatorRef ?? ''}));
  return validate({schema: SESSION_SCHEMA, id: config.id, phase: 'EVALUATING', createdAt: new Date().toISOString(), lockedAt: null,
    criteria: [...config.criteria], evaluators: [...config.evaluators], mapping, ratings: []});
}
function evaluatorPacket(session, evaluatorId) {
  validate(session);
  assert(session.evaluators.includes(evaluatorId), 'UNKNOWN_EVALUATOR');
  return {schema: SESSION_SCHEMA, sessionId: session.id, phase: session.phase, criteria: [...session.criteria],
    candidates: session.mapping.map((x, index) => ({blindId: x.blindId, displayLabel: 'Take ' + String.fromCharCode(65 + index)})),
    completed: session.ratings.filter(x => x.evaluatorId === evaluatorId).map(x => x.blindId),
    notice: 'No audio URLs or filenames in this packet. A trusted operator must supply independently anonymized media.'};
}
function operatorManifest(session) {
  validate(session);
  return {sessionId: session.id, authority: 'OPERATOR_ONLY_DO_NOT_SHARE_WITH_EVALUATORS', mapping: structuredClone(session.mapping)};
}
function submitScores(session, evaluatorId, blindId, scores) {
  validate(session);
  assert(session.phase === 'EVALUATING', 'SESSION_ALREADY_LOCKED');
  const draft = structuredClone(session);
  draft.ratings.push({evaluatorId, blindId, scores: structuredClone(scores)});
  return validate(draft);
}
function missing(session) {
  validate(session);
  const pairs = new Set(session.ratings.map(x => x.evaluatorId + '\0' + x.blindId));
  return session.evaluators.flatMap(evaluatorId => session.mapping
    .filter(v => !pairs.has(evaluatorId + '\0' + v.blindId)).map(v => ({evaluatorId, blindId: v.blindId})));
}
function lock(session) {
  validate(session);
  assert(session.phase === 'EVALUATING', 'SESSION_ALREADY_LOCKED');
  assert(missing(session).length === 0, 'INCOMPLETE_EVALUATION');
  return validate({...structuredClone(session), phase: 'LOCKED', lockedAt: new Date().toISOString()});
}
function reveal(session) {
  validate(session);
  assert(session.phase === 'LOCKED', 'REVEAL_BEFORE_LOCK');
  const rankings = session.mapping.map(m => {
    const ratings = session.ratings.filter(r => r.blindId === m.blindId);
    const average = ratings.reduce((sum, r) => sum + session.criteria.reduce((s, key) => s + r.scores[key], 0) / session.criteria.length, 0) / ratings.length;
    return {sourceId: m.sourceId, blindId: m.blindId, operatorRef: m.operatorRef, average, ratingCount: ratings.length};
  });
  rankings.sort((a, b) => b.average - a.average || a.blindId.localeCompare(b.blindId));
  return {sessionId: session.id, status: 'REVEALED_AFTER_COMPLETE_LOCK', criteria: [...session.criteria], rankings: rankings.map((x, i) => ({rank: i + 1, ...x}))};
}
function importSession(serialized) {
  assert(typeof serialized === 'string' && serialized.length > 0 && serialized.length < 200000, 'INVALID_IMPORT_SIZE');
  let parsed;
  try { parsed = JSON.parse(serialized); } catch { BAD('INVALID_IMPORT_JSON'); }
  return validate(parsed);
}
function exportSession(session) {
  validate(session);
  return JSON.stringify(session); // Owner-only explicit export; never written automatically.
}
module.exports = {SESSION_SCHEMA, createSession, validate, evaluatorPacket, operatorManifest, submitScores, missing, lock, reveal, importSession, exportSession};
