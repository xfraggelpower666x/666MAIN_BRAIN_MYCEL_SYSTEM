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
const containmentStart=main.indexOf('function assertInside(');
const containmentEnd=main.indexOf('\nfunction extractPersonalMilkdropZip(',containmentStart);
assert(containmentStart>=0&&containmentEnd>containmentStart,'archive containment check is available');
const containmentSource=main.slice(containmentStart,containmentEnd);

function fixture(runPowerShell,safeWalkMilkdropLibrary=()=>[{ext:'.milk'}],validateZipEntries=()=>{}){
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
    validateZipEntries,
    personalMilkdropRoot:()=>libraryRoot,
    personalMilkdropLibraryState:()=>({milk:1,milk2:0,count:1}),
    personalMilkdropManifestPath:()=>path.join(libraryRoot,'RADIO-WAVE-PERSONAL-LIBRARY.json'),
    runtimeEvent:(...args)=>events.push(args)
  };
  vm.runInNewContext(`${containmentSource}\n${importerSource}\nthis.importZip=extractPersonalMilkdropZip`,sandbox);
  return {dir,zipPath,libraryRoot,events,importZip:sandbox.importZip};
}

test('preflights ZIP entry count and total uncompressed bytes before extraction',t=>{
  let command='',options,validated='';
  const f=fixture((args,passedOptions)=>{command=args[3];options=passedOptions;return {status:0,stdout:'',stderr:''};},undefined,value=>{validated=value;});
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  const state=f.importZip(f.zipPath);
  assert.deepEqual({...state},{milk:1,milk2:0,count:1});
  assert.equal(validated,f.zipPath);
  assert.equal(options.env.RW_ZIP,f.zipPath);
  assert.equal(options.env.RW_DEST,f.libraryRoot+'-incoming');
  assert(command.includes('$archive=[IO.Compression.ZipFile]::OpenRead($env:RW_ZIP)'));
  assert(command.includes('foreach($entry in $archive.Entries)'));
  assert(command.includes('$entryCount -gt 10000'));
  assert(command.includes('536870912 - $totalBytes'));
  assert(command.indexOf('foreach($entry')<command.indexOf('[IO.Compression.ZipFile]::ExtractToDirectory('));
  assert(command.includes('[IO.Compression.ZipFile]::ExtractToDirectory($env:RW_ZIP, $env:RW_DEST)'));
  assert(fs.existsSync(path.join(f.libraryRoot,'RADIO-WAVE-PERSONAL-LIBRARY.json')));
  assert.equal(f.events.length,1);
});

test('removes partial staging data when extraction fails',t=>{
  let staging='';
  const f=fixture((_args,options)=>{
    staging=options.env.RW_DEST;
    fs.writeFileSync(path.join(staging,'partial.milk'),'partial');
    return {status:1,stderr:'archive extraction failed',stdout:''};
  });
  t.after(()=>fs.rmSync(f.dir,{recursive:true,force:true}));
  assert.throws(()=>f.importZip(f.zipPath),/personal_library_extract_failed:archive extraction failed/);
  assert(staging);
  assert.equal(fs.existsSync(staging),false);
  assert.equal(fs.existsSync(f.libraryRoot),false);
});
