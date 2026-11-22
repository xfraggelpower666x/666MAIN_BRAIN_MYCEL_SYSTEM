#!/usr/bin/env node
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const project=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const load=(p)=>readFileSync(resolve(project,p));
const pointer=JSON.parse(load('CURRENT_POINTER.json'));
function shaGit(buf){return createHash('sha1').update(Buffer.from('blob '+buf.length+'\0')).update(buf).digest('hex')}
const failures=[];
for(const [path,sha] of Object.entries(pointer.files)){try{if(shaGit(load(path))!==sha)failures.push(path+':HASH_MISMATCH')}catch(e){failures.push(path+':MISSING')}}
const cmd=process.argv.slice(2).join(' ').toUpperCase().replace(/^BLISTER TOY /,'')||'HELP';
const valid=['SYSTEMSTART','STATUS','HELP','WEITER','NEW CHAT','UPDATE'];
if(!valid.includes(cmd)){console.error('Unknown project command');process.exit(2)}
if(failures.length){console.error(JSON.stringify({state:'CONFLICT_QUARANTINE',failures},null,2));process.exit(1)}
const handoff=JSON.parse(load('continuity/CURRENT_HANDOFF.json'));
const status={system_id:pointer.system_id,release:pointer.release,state:'LOCAL_POINTER_VERIFIED',files_checked:Object.keys(pointer.files).length,host_adoption:'OPEN',repo_readback:'REQUIRES_FRESH_GITHUB_CHECK'};
if(cmd==='HELP')console.log(valid.map(x=>'BLISTER TOY '+x).join('\n'));
else if(cmd==='WEITER')console.log(JSON.stringify({status,next:handoff.next_evidenced_step},null,2));
else if(cmd==='NEW CHAT')console.log(JSON.stringify({bootstrap_order:pointer.bootstrap_order,return_anchor:handoff.next_evidenced_step},null,2));
else if(cmd==='UPDATE')console.log('WRITE_GATED: fresh repo HEAD, project scope and explicit update governance required');
else console.log(JSON.stringify({...status,bootstrap_order:cmd==='SYSTEMSTART'?pointer.bootstrap_order:undefined},null,2));
