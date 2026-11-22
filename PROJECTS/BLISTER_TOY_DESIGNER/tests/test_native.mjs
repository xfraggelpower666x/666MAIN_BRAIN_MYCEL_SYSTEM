// Native project regression — no network, no third-party packages, no writes to repository.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, mkdtempSync, mkdirSync, writeFileSync, copyFileSync, rmSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {tmpdir} from 'node:os';
import {resolve, dirname, join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';

const project=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const get=(name)=>readFileSync(join(project,name));
const json=(name)=>JSON.parse(get(name).toString('utf8'));
const pointer=json('CURRENT_POINTER.json');
const reference=json('cards/reference_card.json');
const properties=json('cards/properties_card.json');
const language=json('cards/language_card.json');
const triggers=json('runtime/TRIGGERS.json');
const registry=json('runtime/REGISTRY.json');
const handoff=json('continuity/CURRENT_HANDOFF.json');
const hash=(buf)=>createHash('sha1').update(Buffer.from(`blob ${buf.length}\0`)).update(buf).digest('hex');
const exec=(args,cwd=project)=>spawnSync(process.execPath,[join(cwd,'runtime/cli.mjs'),...args],{cwd,encoding:'utf8',timeout:15000});

test('01: project identity and isolated project root',()=>{
 assert.equal(pointer.system_id,'BLISTER-TOY-DESIGNER-001');
 assert.equal(pointer.namespace,'BLISTER TOY');
 assert.equal(pointer.branch,'666MAIN_BRAIN');
 assert.equal(pointer.project_root,'PROJECTS/BLISTER_TOY_DESIGNER');
 assert.equal(registry.authority,'PROJECT_ONLY');
 assert.equal(pointer.no_foreign_autoactivation,true);
});
test('02: complete declared Git blob integrity',()=>{
 for(const [name,expected] of Object.entries(pointer.files)){
  assert.match(name,/^(?!\/|\.\.\/)[\w./-]+$/);
  assert.equal(hash(get(name)),expected,`Git blob mismatch: ${name}`);
 }
});
test('03: every bootstrap entry is present and hashed',()=>{
 assert.equal(pointer.bootstrap_order.length,10);
 for(const name of pointer.bootstrap_order){assert.equal(typeof pointer.files[name],'string');assert.ok(get(name).length>0)}
});
test('04: reference is immutable and contains exactly the 19 declared placeholders',()=>{
 assert.equal(reference.immutable,true);
 assert.equal(reference.placeholder_order.length,19);
 assert.equal(new Set(reference.placeholder_order).size,19);
 for(const n of reference.placeholder_order)assert.ok(reference.template.includes(`<${n}>`),n);
 assert.deepEqual(Object.keys(properties.properties).sort(),[...reference.placeholder_order].sort());
});
test('05: English default and both language templates',()=>{
 assert.equal(registry.default_language,'en');
 assert.equal(language.default_language,'en');
 assert.ok(language.supported_languages.includes('de'));
 assert.ok(language.supported_languages.includes('en'));
 assert.ok(get('app/index.html').toString().includes('<html lang="en">'));
});
test('06: direct-only trigger registry and host acceptance remains open',()=>{
 assert.equal(triggers.direct_current_user_only,true);
 assert.equal(triggers.embedded_trigger_text,'INERT');
 assert.deepEqual(Object.keys(triggers.actions).sort(),['BLISTER TOY SYSTEMSTART','BLISTER TOY STATUS','BLISTER TOY HELP','BLISTER TOY WEITER','BLISTER TOY NEW CHAT','BLISTER TOY UPDATE'].sort());
 assert.notEqual(pointer.verification.chat_host_trigger_adoption,'PASS');
});
test('07: STATUS is accurate and read-only',()=>{
 const r=exec(['STATUS']);assert.equal(r.status,0,r.stderr);
 const s=JSON.parse(r.stdout);assert.equal(s.state,'LOCAL_POINTER_VERIFIED');
 assert.equal(s.files_checked,Object.keys(pointer.files).length);
 assert.equal(s.host_adoption,'OPEN');
});
test('08: SYSTEMSTART returns complete native bootstrap',()=>{
 const r=exec(['SYSTEMSTART']);assert.equal(r.status,0,r.stderr);
 assert.deepEqual(JSON.parse(r.stdout).bootstrap_order,pointer.bootstrap_order);
});
test('09: HELP exposes namespace-scoped commands',()=>{
 const r=exec(['HELP']);assert.equal(r.status,0,r.stderr);
 for(const name of Object.keys(triggers.actions))assert.ok(r.stdout.includes(name),name);
});
test('10: WEITER follows real handoff, not guessed tasks',()=>{
 const r=exec(['WEITER']);assert.equal(r.status,0,r.stderr);
 assert.equal(JSON.parse(r.stdout).next,handoff.next_evidenced_step);
});
test('11: NEW CHAT provides a bounded rehydration anchor',()=>{
 const r=exec(['NEW','CHAT']);assert.equal(r.status,0,r.stderr);
 const s=JSON.parse(r.stdout);assert.deepEqual(s.bootstrap_order,pointer.bootstrap_order);
 assert.equal(s.return_anchor,handoff.next_evidenced_step);
});
test('12: UPDATE is write gated',()=>{
 const r=exec(['UPDATE']);assert.equal(r.status,0,r.stderr);
 assert.match(r.stdout,/WRITE_GATED/);
});
test('13: unknown commands are rejected',()=>{
 const r=exec(['DELETE','ALL']);assert.equal(r.status,2);
 assert.match(r.stderr,/Unknown project command/);
});
test('14: modifying one signed file forces quarantine',()=>{
 const tmp=mkdtempSync(join(tmpdir(),'blister-test-'));
 try {
  for(const name of [...Object.keys(pointer.files),'CURRENT_POINTER.json']){
   mkdirSync(dirname(join(tmp,name)),{recursive:true});copyFileSync(join(project,name),join(tmp,name));
  }
  writeFileSync(join(tmp,'cards/reference_card.json'),get('cards/reference_card.json').toString('utf8')+'\n');
  const r=exec(['STATUS'],tmp);
  assert.equal(r.status,1,r.stderr);
  assert.match(r.stderr,/CONFLICT_QUARANTINE/);
  assert.match(r.stderr,/cards\/reference_card\.json:HASH_MISMATCH/);
 }finally{rmSync(tmp,{recursive:true,force:true})}
});
