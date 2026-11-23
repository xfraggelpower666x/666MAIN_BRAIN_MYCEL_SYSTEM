'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const ab = require('../src/blind_ab.js');
const {boot} = require('../src/bootstrap.js');
const cli = require('../cli.js');
const config = () => ({id: 'session-1', candidates: [
  {id: 'weirdness-40', operatorRef: 'private_weirdness_40.wav'},
  {id: 'weirdness-70', operatorRef: 'private_weirdness_70.wav'}],
  evaluators: ['A', 'B'], criteria: ['mix', 'impact', 'intelligibility']});
const fresh = () => ab.createSession(config());
function fullyRated(initial) {
  let s = initial;
  for (const e of s.evaluators) for (const m of s.mapping) {
    s = ab.submitScores(s, e, m.blindId, {mix: 70, impact: 80, intelligibility: 90});
  }
  return s;
}
test('R02 bootstrap binds verified R01 and explicitly forbids historical promotion', () => {
  const b = boot();
  assert.equal(b.production, false);
  assert.equal(b.historicalReadback, 'PENDING');
  assert.equal(b.report.entries, 28);
  assert.equal(b.report.sources, 25);
  assert.equal(b.search('psycho').some(x => x.type === 'prompt'), true);
  assert.equal(typeof b.blindAB.createSession, 'function');
});
test('R02 CLI status is no production claim', () => {
  const s = cli.run(['status']); assert.equal(s.release, 'DEVELOPMENT_CANDIDATE');
  assert.equal(s.production, false); assert.equal(s.research.topics, 2);
});
test('R02 CLI rejects mutation commands', () => assert.throws(() => cli.run(['write','foo']), /USAGE/));
test('session starts evaluating with two cryptographically randomized anonymous variants', () => {
  const s = fresh();
  assert.equal(s.phase, 'EVALUATING'); assert.equal(s.mapping.length, 2);
  assert.ok(s.mapping.every(m => /^B-[0-9a-f-]{36}$/.test(m.blindId)));
  assert.notEqual(s.mapping[0].blindId, s.mapping[1].blindId);
});
test('no candidate data leaked in evaluator packet', () => {
  const s = fresh(); const p = ab.evaluatorPacket(s, 'A'); const json = JSON.stringify(p);
  assert.doesNotMatch(json, /weirdness|private_|sourceId|operatorRef|\.wav/);
  assert.equal(p.candidates.length, 2);
  assert.deepEqual(p.candidates.map(x=>x.displayLabel), ['Take A', 'Take B']);
});
test('operator manifest clearly separated from evaluator packet', () => {
  const s = fresh();
  assert.equal(ab.operatorManifest(s).mapping.length, 2);
  assert.ok(ab.operatorManifest(s).authority.includes('DO_NOT_SHARE'));
});
test('wrong evaluator refuses evaluator packet', () => {
  assert.throws(() => ab.evaluatorPacket(fresh(), 'Z'), /UNKNOWN_EVALUATOR/);
});
test('incomplete coverage blocks lock and reveal', () => {
  const s = fresh(); const one = ab.submitScores(s, 'A', s.mapping[0].blindId, {mix: 1,impact: 2,intelligibility: 3});
  assert.equal(one.ratings.length, 1); assert.equal(s.ratings.length, 0);
  assert.equal(ab.missing(one).length, 3);
  assert.throws(() => ab.lock(one), /INCOMPLETE_EVALUATION/);
  assert.throws(() => ab.reveal(one), /REVEAL_BEFORE_LOCK/);
});
test('non-finite/incorrect-score ranges are rejected', () => {
  const s = fresh(); const b=s.mapping[0].blindId;
  for (const bad of [NaN, Infinity, -Infinity, null, '50', -0.1, 100.1]) {
    assert.throws(() => ab.submitScores(s,'A',b,{mix:bad, impact:40, intelligibility:40}), /INVALID_SCORE/);
  }
});
test('missing criteria and unexpected criteria blocked', () => {
  const s = fresh(); const b=s.mapping[0].blindId;
  assert.throws(() => ab.submitScores(s,'A',b,{mix:40,impact:60}), /INCOMPLETE_CRITERIA/);
  assert.throws(() => ab.submitScores(s,'A',b,{mix:40,impact:60,intelligibility:80,extra:0}), /INCOMPLETE_CRITERIA/);
});
test('duplicate evaluator/variant score cannot overwrite prior value', () => {
  const s=fresh(); const b=s.mapping[0].blindId;
  const one=ab.submitScores(s,'A',b,{mix:90,impact:90,intelligibility:90});
  assert.throws(()=>ab.submitScores(one,'A',b,{mix:0,impact:0,intelligibility:0}),/DUPLICATE_RATING/);
});
test('unknown evaluator and blind ID blocked', () => {
  const s=fresh(); const scores={mix:10,impact:10,intelligibility:10};
  assert.throws(()=>ab.submitScores(s,'C',s.mapping[0].blindId,scores),/UNREGISTERED_RATING/);
  assert.throws(()=>ab.submitScores(s,'A','B-wrong',scores),/UNREGISTERED_RATING/);
});
test('complete session can be locked and revealed with correct counts', () => {
  const rated=fullyRated(fresh()); assert.equal(ab.missing(rated).length,0);
  const locked=ab.lock(rated); assert.equal(locked.phase,'LOCKED'); assert.equal(rated.phase,'EVALUATING');
  const result=ab.reveal(locked); assert.equal(result.rankings.length,2);
  assert.equal(result.rankings[0].average,80);
  assert.equal(result.rankings[0].ratingCount,2);
  assert.deepEqual(result.rankings.map(x=>x.rank),[1,2]);
});
test('cannot edit, resubmit or double lock after lock', () => {
  const s=ab.lock(fullyRated(fresh()));
  assert.throws(()=>ab.submitScores(s,'A',s.mapping[0].blindId,{mix:80,impact:80,intelligibility:80}),/SESSION_ALREADY_LOCKED/);
  assert.throws(()=>ab.lock(s),/SESSION_ALREADY_LOCKED/);
});
test('snapshot import/export round-trip and locked state valid', () => {
  const s=ab.lock(fullyRated(fresh())); const restored=ab.importSession(ab.exportSession(s));
  assert.deepEqual(restored,s);
  assert.equal(ab.reveal(restored).rankings.length,2);
});
test('import rejects malformed JSON, oversized or unsupported schema', () => {
  assert.throws(()=>ab.importSession('oops'),/INVALID_IMPORT_JSON/);
  assert.throws(()=>ab.importSession('x'.repeat(200000)),/INVALID_IMPORT_SIZE/);
  const fake=fresh(); fake.schema='historical/1.7.1';
  assert.throws(()=>ab.importSession(JSON.stringify(fake)),/INVALID_SESSION_SCHEMA/);
});
test('import cannot lock a partial session', () => {
  const s=fresh();s.phase='LOCKED';s.lockedAt=new Date().toISOString();
  assert.throws(()=>ab.importSession(JSON.stringify(s)),/LOCKED_WITH_MISSING_RATINGS/);
});
test('import rejects duplicate mapping / missing original', () => {
  const s=fresh();s.mapping[1].sourceId=s.mapping[0].sourceId;
  assert.throws(()=>ab.importSession(JSON.stringify(s)),/DUPLICATE_MAPPING/);
});
test('import cannot contain extra keys, prototype poison or fake ratings', () => {
  const s=fresh(); s.extra='unexpected';
  assert.throws(()=>ab.importSession(JSON.stringify(s)),/UNKNOWN_FIELD/);
  const injected=JSON.stringify(fresh()).replace('"schema"', '"__proto__": {}, "schema"');
  assert.throws(()=>ab.importSession(injected),/UNKNOWN_FIELD/);
});
test('invalid identifiers, duplicate evaluator, single candidate rejected', () => {
  const c=config();c.candidates=c.candidates.slice(0,1);
  assert.throws(()=>ab.createSession(c),/INVALID_VARIANT_COUNT/);
  const c2=config();c2.evaluators=['A','A']; assert.throws(()=>ab.createSession(c2),/INVALID_EVALUATORS/);
  const c3=config();c3.id='../escape';assert.throws(()=>ab.createSession(c3),/INVALID_SESSION_ID/);
});
test('invalid operatorRef control characters rejected', () => {
  const c=config();c.candidates[0].operatorRef='a\nsecret';
  assert.throws(()=>ab.createSession(c),/INVALID_OPERATOR_REF/);
});
test('evaluator packet after rating shows only completion IDs not scores', () => {
  const s=fresh(); const one=ab.submitScores(s,'A',s.mapping[0].blindId,{mix:12,impact:32,intelligibility:45});
  const packet=ab.evaluatorPacket(one,'A');
  assert.equal(packet.completed.length,1); assert.ok(!Object.hasOwn(packet,'ratings'));
});
test('source code contains no persistence or network calls', () => {
  const fs=require('node:fs'), path=require('node:path');
  for(const f of ['../src/blind_ab.js','../src/bootstrap.js','../cli.js']) {
    const content=fs.readFileSync(path.resolve(__dirname,f),'utf8');
    assert.doesNotMatch(content, /writeFile|appendFile|unlinkSync|rmSync|fetch\(|http\.request|https\.request|child_process/);
  }
});
