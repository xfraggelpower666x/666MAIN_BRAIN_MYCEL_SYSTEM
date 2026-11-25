const {test}=require('node:test'),assert=require('node:assert/strict');
const {KEYS,id3Fields}=require('../electron/id3.cjs');
test('all nine original ID3 fields',()=>{const x=Object.fromEntries(KEYS.map(k=>[k,'value']));assert.equal(KEYS.length,9);assert.deepEqual(id3Fields(x),x)});
test('omission preserves and explicit empty clears',()=>assert.deepEqual(id3Fields({TIT2:''}),{TIT2:''}));
test('invalid payload rejected',()=>{for(const x of [{},{title:'x'},{TIT2:4},{TIT2:'\0'},{TIT2:'x'.repeat(2049)},null,[]])assert.throws(()=>id3Fields(x))});
