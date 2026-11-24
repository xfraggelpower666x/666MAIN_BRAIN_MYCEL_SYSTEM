/** CODING PROFI R04: additive, source-owned, unpacked Git tree mirror. */
import {pathToFileURL} from 'node:url';
const OWNER='xfraggelpower666x',REPO='666MAIN_BRAIN_MYCEL_SYSTEM',BRANCH='666MAIN_BRAIN';
const HEX=/^[0-9a-f]{40}$/;
export function treeSha(entries,name){
  const x=entries?.find(x=>x.path===name);
  if(!x||x.type!=='tree'||!HEX.test(x.sha))throw Error('REQUIRED_TREE_MISSING:'+name);
  return x.sha;
}
export function compareTrees(a,b){
  if(!HEX.test(a)||!HEX.test(b))throw Error('INVALID_TREE_SHA');
  return a===b?'UNCHANGED_VERIFIED':'BACKUP_SYNC_REQUIRED';
}
export function githubApi(token,request=fetch){
  if(!token)throw Error('GITHUB_TOKEN_MISSING');
  const root='https://api.github.com/repos/'+OWNER+'/'+REPO;
  return async(method,path,data)=>{
    const r=await request(root+path,{method,headers:{
      Authorization:'Bearer '+token,Accept:'application/vnd.github+json',
      'X-GitHub-Api-Version':'2022-11-28',
      ...(data?{'Content-Type':'application/json'}:{})
    },...(data?{body:JSON.stringify(data)}:{})});
    if(!r.ok){const e=Error('GITHUB_HTTP_'+r.status);e.status=r.status;throw e;}
    return r.json();
  };
}
export async function inspect(api){
  const ref=await api('GET','/git/ref/heads/'+BRANCH);
  const head=ref.object?.sha;if(!HEX.test(head))throw Error('HEAD_NOT_VERIFIED');
  const commit=await api('GET','/git/commits/'+head);
  const rootSha=commit.tree?.sha;if(!HEX.test(rootSha))throw Error('ROOT_NOT_VERIFIED');
  const root=await api('GET','/git/trees/'+rootSha);
  const projects=await api('GET','/git/trees/'+treeSha(root.tree,'PROJECTS'));
  const source=treeSha(projects.tree,'LYVRA_CODING_PROFI');
  const backup=await api('GET','/git/trees/'+treeSha(projects.tree,'666_CODEFORGE_ALLIANCE'));
  const mirror=treeSha(backup.tree,'CODING_PROFI_LIVE');
  return {head,rootSha,source,mirror};
}
export async function sync(api){
  const s=await inspect(api);
  if(compareTrees(s.source,s.mirror)==='UNCHANGED_VERIFIED')
    return {status:'UNCHANGED_VERIFIED',head:s.head,tree:s.source};
  const t=await api('POST','/git/trees',{base_tree:s.rootSha,tree:[{
    path:'PROJECTS/666_CODEFORGE_ALLIANCE/CODING_PROFI_LIVE',
    mode:'040000',type:'tree',sha:s.source
  }]});
  if(!HEX.test(t.sha))throw Error('CANDIDATE_TREE_INVALID');
  const c=await api('POST','/git/commits',{message:'backup(coding-profi): sync unpacked live source tree [skip ci]',tree:t.sha,parents:[s.head]});
  if(!HEX.test(c.sha))throw Error('CANDIDATE_COMMIT_INVALID');
  // GitHub rejects a non-fast-forward ref update, so concurrent writes are not overwritten.
  await api('PATCH','/git/refs/heads/'+BRANCH,{sha:c.sha,force:false});
  const observed=await inspect(api);
  if(observed.source!==observed.mirror)throw Error('BACKUP_SYNC_READBACK_PENDING');
  return {status:'BACKUP_SYNC_VERIFIED',commit:c.sha,observedHead:observed.head,
    sourceTree:observed.source,backupTree:observed.mirror};
}
export async function run(token,request=fetch){
  const api=githubApi(token,request);
  for(let attempt=0;attempt<3;attempt++){
    try{return await sync(api);}
    catch(e){
      if((e.status===409||e.status===422)&&attempt<2)continue;
      throw e;
    }
  }
  throw Error('CONFLICT_QUARANTINE');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  run(process.env.GITHUB_TOKEN).then(x=>console.log(JSON.stringify(x)))
    .catch(e=>{console.error(e.message);process.exitCode=1;});
}
