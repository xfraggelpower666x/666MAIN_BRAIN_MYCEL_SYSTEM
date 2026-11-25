const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {required,resolveLayout}=require('../electron/source-layout.cjs');
function fixture(fn){const root=fs.mkdtempSync(path.join(os.tmpdir(),'lyvra-layout-'));try{fn(root)}finally{fs.rmSync(root,{recursive:true,force:true})}}
function fill(root,mode,keys=Object.keys(required)){for(const k of keys){const p=path.join(root,mode,required[k]);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,'fixture')}}
test('complete originals preferred',()=>fixture(r=>{fill(r,'imports');fill(r,'originals');assert.equal(resolveLayout(r).mode,'originals')}));
test('partial originals fall back to complete imports',()=>fixture(r=>{fill(r,'originals',['mp']);fill(r,'imports');assert.equal(resolveLayout(r).mode,'imports')}));
test('never combine partial source trees',()=>fixture(r=>{fill(r,'originals',['mp']);fill(r,'imports',Object.keys(required).filter(k=>k!=='mp'));assert.throws(()=>resolveLayout(r),/Unvollständiger/)}));
test('missing boot blocks startup',()=>fixture(r=>{fill(r,'originals',Object.keys(required).filter(k=>k!=='boot'));assert.throws(()=>resolveLayout(r),/boot/)}));
