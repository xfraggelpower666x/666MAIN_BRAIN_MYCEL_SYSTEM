"""R02/R03 regression scenarios. Synthetic fixtures, never production writes."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from parity import audit, blob

class ParityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.identity={'system_id':'666TDI-001'}
        self.put('identity/CHARACTER.json',dict(self.identity,pronoun_de='er'))
        self.put('triggers/TRIGGER_REGISTRY.json',dict(self.identity,direct_chat_triggers=['KAIRON STATUS']))
        e={'seq':1,'prev_hash':'GENESIS','kind':'TEST'}
        e['hash']=hashlib.sha256(json.dumps(e,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.put('livecircle/CURRENT_STATE.json',dict(self.identity,foreign_repo_write_allowed=False,revision=1,events=[e]))
        self.put('native/musical_intelligence/A.json',{})
        self.p=dict(self.identity,native_musical_intelligence_r01={'root':'PROJECTS/KAIRON/native/musical_intelligence/','bindings':{'A.json':blob(self.read('native/musical_intelligence/A.json'))}})
        self.put('CURRENT_POINTER.json',self.p)
        sha=blob(self.read('CURRENT_POINTER.json'))
        self.put('windows_studio/NATIVE_BINDING.json',dict(self.identity,pointer_git_blob_sha1=sha,expected_nmi_revisions=1,expected_nmi_bindings=1))
        self.put('plugin/release-binding.json',dict(self.identity,canonical_pointer_blob=sha))
    def put(self,name,obj):
        p=self.root/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(obj),encoding='utf-8')
    def read(self,name): return (self.root/name).read_bytes()
    def test_valid(self):
        self.assertEqual(audit(self.root)['status'],'SOURCE_BINDINGS_ALIGNED')
    def test_nmi_tamper(self):
        self.put('native/musical_intelligence/A.json',{'changed':True})
        with self.assertRaisesRegex(ValueError,'NMI_HASH'): audit(self.root)
    def test_duplicate_trigger(self):
        self.put('triggers/TRIGGER_REGISTRY.json',dict(self.identity,direct_chat_triggers=['KAIRON STATUS']*2))
        with self.assertRaisesRegex(ValueError,'TRIGGER_REGISTRY'): audit(self.root)
    def test_chain_tamper(self):
        c=json.loads(self.read('livecircle/CURRENT_STATE.json'))
        c['events'][0]['kind']='CHANGED'
        self.put('livecircle/CURRENT_STATE.json',c)
        with self.assertRaisesRegex(ValueError,'LIVE_CIRCLE_CHAIN'): audit(self.root)
    def test_evolution_pending(self):
        self.p['native_musical_intelligence_r02']=self.p['native_musical_intelligence_r01']
        self.put('CURRENT_POINTER.json',self.p)
        self.assertEqual(audit(self.root)['status'],'NATIVE_EVOLUTION_PENDING')
    def test_revision_gap(self):
        self.p['native_musical_intelligence_r03']=self.p['native_musical_intelligence_r01']
        self.put('CURRENT_POINTER.json',self.p)
        with self.assertRaisesRegex(ValueError,'NMI_SEQUENCE'): audit(self.root)
    def test_foreign_identity(self):
        self.put('identity/CHARACTER.json',{'system_id':'FOREIGN','pronoun_de':'er'})
        with self.assertRaisesRegex(ValueError,'FOREIGN_IDENTITY'): audit(self.root)
if __name__=='__main__': unittest.main()
