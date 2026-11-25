'use strict';
const KEYS=Object.freeze(['TIT2','TPE1','TPE2','TALB','TCON','TCOM','TDRC','TRCK','TPOS']);
function id3Fields(input){
 if(!input||typeof input!=='object'||Array.isArray(input))throw Error('ID3-Feldauswahl fehlt');
 const entries=Object.entries(input);
 if(!entries.length)throw Error('Keine ID3-Felder ausgewählt');
 for(const [k,v] of entries)if(!KEYS.includes(k)||typeof v!=='string'||v.length>2048||v.includes('\0'))throw Error('Ungültiges ID3-Feld');
 return Object.fromEntries(entries);
}
module.exports={KEYS,id3Fields};
