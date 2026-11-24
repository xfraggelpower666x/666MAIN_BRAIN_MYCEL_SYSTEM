import test from 'node:test';
import assert from 'node:assert/strict';
import {treeSha,compareTrees,githubApi,sync} from './sync-live-backup.mjs';
const S='a'.repeat(40),M='b'.repeat(40),H='c'.repeat(40),R='d'.repeat(40),P='e'.repeat(40),B='f'.repeat(40),T='1'.repeat(40),C='2'.repeat(40);
function fixture(equal=false){
  let published=false;const events=[];
  const api=async(method,path,data)=>{
    events.push({method,path,data});
    if(method==='GET'&&path.endsWith('/git/ref/heads/666MAIN_BRAIN'))return {object:{sha:published?C:H}};
    if(method==='GET'&&path==='/git/commits/'+H)return {tree:{sha:R}};
    if(method==='GET'&&path==='/git/commits/'+C)return {tree:{sha:T}};
    if(method==='GET'&&(path==='/git/trees/'+R||path==='/git/trees/'+T))return {tree:[{path:'PROJECTS',type:'tree',sha:P}]};
    if(method==='GET'&&path==='/git/trees/'+P)return {tree:[{path:'LYVRA_CODING_PROFI',type:'tree',sha:S},{path:'666_CODEFORGE_ALLIANCE',type:'tree',sha:B}]};
    if(method==='GET'&&path==='/git/trees/'+B)return {tree:[{path:'CODING_PROFI_LIVE',type:'tree',sha:published||equal?S:M}]};
    if(method==='POST'&&path==='/git/trees')return {sha:T};
    if(method==='POST'&&path==='/git/commits')return {sha:C};
    if(method==='PATCH'&&path.endsWith('/git/refs/heads/666MAIN_BRAIN')){published=true;return {object:{sha:C}};}
    throw Error('UNEXPECTED:'+method+':'+path);
  };
  return {api,events};
}
test('equal full trees perform no writes',async()=>{
 const f=fixture(true),r=await sync(f.api);assert.equal(r.status,'UNCHANGED_VERIFIED');
 assert.equal(f.events.filter(x=>x.method!=='GET').length,0);
});
test('unequal tree publishes exact source tree and reads back',async()=>{
 const f=fixture(),r=await sync(f.api);assert.equal(r.status,'BACKUP_SYNC_VERIFIED');
 assert.equal(r.sourceTree,r.backupTree);
 const t=f.events.find(x=>x.method==='POST'&&x.path==='/git/trees');
 assert.equal(t.data.tree[0].sha,S);assert.equal(t.data.tree[0].path,'PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE');
 assert.equal(f.events.find(x=>x.method==='PATCH').data.force,false);
});
test('invalid tree rejected',()=>assert.throws(()=>treeSha([], 'PROJECTS'),/REQUIRED_TREE_MISSING/));
test('mutable SHA rejected',()=>assert.throws(()=>compareTrees('HEAD',S),/INVALID_TREE_SHA/));
test('missing token rejected',()=>assert.throws(()=>githubApi(''),/GITHUB_TOKEN_MISSING/));
test('only own repo and backup target accessed',async()=>{
 const f=fixture();await sync(f.api);
 assert.equal(f.events.filter(x=>x.method==='POST'&&x.path==='/git/trees').length,1);
 assert.equal(f.events.filter(x=>x.method==='PATCH').length,1);
});
