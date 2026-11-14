'use strict';

const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const vm=require('node:vm');
const {test}=require('node:test');

const root=path.resolve(__dirname,'..');
const main=fs.readFileSync(path.join(root,'main.js'),'utf8');
const start=main.indexOf('function extractPersonalMilkdropZip(');
const end=main.indexOf("\n\nregisterIpc('dialog:openMilkdropPack'",start);
assert(start>=0&&end>start,'personal MilkDrop ZIP importer is available');
const importerSource=main.slice(start,end);

function fixture(runPowerShell,safeWalkMilkdropLibrary=()=>[{ext:'.milk'}]){
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'radio-wave-milkdrop-'));
  const zipPath=path.join(dir,"source's-pack.zip");
  fs.writeFileSync(zipPath,'zip fixture');
  const libraryRoot=path.join(dir,'library');
  const events=[];
  const sandbox={
    process:{platform:'win32'},
    fs,
    path,
    runPowerShell,
    safeWalkMilkdropLibrary,
    personalMilkdropRoot:()=>libraryRoot,
    personalMilkdropLibraryState:()=>({milk:1,milk2:0,count:1}),
    personalMilkdropManifestPath:()=>path.join(libraryRoot,'RADIO-WAVE-PERSONAL-LIBRARY.json'),
    runtimeEvent:(...args)=>events.push(args)
  };
  vm.runInNewContext(`${importerSource}\nthis.importZip=extractPersonalMilkdropZip`,sandbox);
  return {dir,zipPath,libraryRoot,events,importZip:sandbox.importZip};
}

test('preflights ZIP entry count and total uncompressed bytes before extraction',t=>{
  let command='';
  const f=fixture(args=>{command=args[3];return {status:0,stdout:'',stderr:''};});
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  const state=f.importZip(f.zipPath);
  assert.deepEqual({...state},{milk:1,milk2:0,count:1});
  assert(command.includes('$archive=[IO.Compression.ZipFile]::OpenRead('));
  assert(command.includes('foreach($entry in $archive.Entries)'));
  assert(command.includes('$entryCount -gt 10000'));
  assert(command.includes('536870912 - $totalBytes'));
  assert(command.indexOf('foreach($entry')<command.indexOf('[IO.Compression.ZipFile]::ExtractToDirectory('));
  assert(fs.existsSync(path.join(f.libraryRoot,'RADIO-WAVE-PERSONAL-LIBRARY.json')));
  assert.equal(f.events.length,1);
});

test('removes partial staging data when extraction fails',t=>{
  let staging='';
  const f=fixture(args=>{
    const script=args[3];
    staging=script.match(/ExtractToDirectory\([\s\S]*, '([^']+)'\)/)[1];
    fs.writeFileSync(path.join(staging,'partial.milk'),'partial');
    return {status:1,stderr:'archive extraction failed',stdout:''};
  });
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  assert.throws(()=>f.importZip(f.zipPath),/personal_library_extract_failed:archive extraction failed/);
  assert(staging);
  assert.equal(fs.existsSync(staging),false);
  assert.equal(fs.existsSync(f.libraryRoot),false);
});

test('keeps the previous presets when the new library cannot be promoted',t=>{
  const originalRename=fs.renameSync;
  const f=fixture(()=>({status:0,stdout:'',stderr:''}));
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  fs.mkdirSync(f.libraryRoot);
  const original=path.join(f.libraryRoot,'old.milk');
  fs.writeFileSync(original,'previous preset');
  t.mock.method(fs,'renameSync',(from,to)=>{
    if(from===f.libraryRoot+'-incoming'&&to===f.libraryRoot)throw new Error('promotion failed');
    return originalRename(from,to);
  });

  assert.throws(()=>f.importZip(f.zipPath),/promotion failed/);
  assert.equal(fs.readFileSync(original,'utf8'),'previous preset');
  assert.equal(fs.existsSync(f.libraryRoot+'-incoming'),false);
  assert.equal(f.events.length,0);
});

test('restores previous presets when the new manifest cannot be written',t=>{
  const f=fixture(()=>({status:0,stdout:'',stderr:''}));
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  fs.mkdirSync(f.libraryRoot);
  const original=path.join(f.libraryRoot,'old.milk');
  fs.writeFileSync(original,'previous preset');
  t.mock.method(fs,'writeFileSync',()=>{throw new Error('manifest failed');});

  assert.throws(()=>f.importZip(f.zipPath),/manifest failed/);
  assert.equal(fs.readFileSync(original,'utf8'),'previous preset');
  assert.equal(fs.readdirSync(f.dir).some(name=>name.startsWith('library-backup-')),false);
  assert.equal(f.events.length,0);
});

test('keeps the recovery directory when rollback cannot rename it back',t=>{
  const originalRename=fs.renameSync;
  const f=fixture(()=>({status:0,stdout:'',stderr:''}));
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  fs.mkdirSync(f.libraryRoot);
  fs.writeFileSync(path.join(f.libraryRoot,'old.milk'),'previous preset');
  t.mock.method(fs,'renameSync',(from,to)=>{
    if(to===f.libraryRoot)throw new Error('destination unavailable');
    return originalRename(from,to);
  });

  assert.throws(()=>f.importZip(f.zipPath),/personal_library_rollback_failed/);
  const backup=fs.readdirSync(f.dir).find(name=>name.startsWith('library-backup-'));
  assert(backup);
  assert.equal(fs.readFileSync(path.join(f.dir,backup,'library','old.milk'),'utf8'),'previous preset');
  assert.equal(f.events.length,0);
});

test('cleans up the backup after a successful replacement',t=>{
  const f=fixture(()=>({status:0,stdout:'',stderr:''}));
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  fs.mkdirSync(f.libraryRoot);
  fs.writeFileSync(path.join(f.libraryRoot,'old.milk'),'previous preset');

  f.importZip(f.zipPath);
  assert(fs.existsSync(path.join(f.libraryRoot,'RADIO-WAVE-PERSONAL-LIBRARY.json')));
  assert.equal(fs.readdirSync(f.dir).some(name=>name.startsWith('library-backup-')),false);
  assert.equal(f.events.length,1);
});
