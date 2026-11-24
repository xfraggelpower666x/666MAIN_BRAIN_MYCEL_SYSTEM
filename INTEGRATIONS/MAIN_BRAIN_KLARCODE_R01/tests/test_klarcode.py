import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from klarcode.engine import GateError, Manager, safe_relative

class TestKlarcode(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.man = Manager(self.root)
        self.source = self.root/'incoming'
        self.source.mkdir()
        (self.source/'main.py').write_text('print("live")\n')

    def mini(self):
        self.man.register('MINI_01','MINI-OWNER','LOCAL_MINI')
        return self.man.status('MINI_01')

    def test_register_live_mini(self):
        a=self.mini()
        self.assertEqual(a['revision'],0)
        self.assertTrue((self.root/'PROJECTS/MINI_01/LIVECIRCLE.json').exists())
    def test_save_release_and_readback(self):
        a=self.mini()
        r=self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
        self.assertEqual(r['status'],'VERIFIED')
        b=self.man.status('MINI_01')
        self.assertEqual(b['release'],r['release'])
        self.assertEqual(b['files'],1)
        self.assertEqual(b['revision'],1)
        self.assertEqual(b['livecircle']['return_anchor'], 'RELEASE:' + r['release'])
    def test_stale_pointer_fails(self):
        a=self.mini()
        self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
        (self.source/'main.py').write_text('print("other")')
        with self.assertRaises(GateError): self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
    def test_wrong_owner_fails(self):
        a=self.mini()
        with self.assertRaises(GateError): self.man.save('MINI_01',self.source,owner='OTHER',expected_pointer=a['pointer_sha256'])
    def test_duplicate_release_fails(self):
        a=self.mini()
        self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
        b=self.man.status('MINI_01')
        with self.assertRaises(GateError): self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=b['pointer_sha256'])
    def test_tampered_code_fails(self):
        a=self.mini()
        r=self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
        p=self.root/'PROJECTS/MINI_01/releases'/r['release']/'src/main.py'
        p.write_text('tampered')
        with self.assertRaises(GateError): self.man.status('MINI_01')
    def test_livecircle_drift_fails(self):
        self.mini()
        (self.root/'PROJECTS/MINI_01/LIVECIRCLE.json').write_text('{}')
        with self.assertRaises(GateError): self.man.status('MINI_01')
    def test_secret_filename_rejected(self):
        a=self.mini()
        (self.source/'.env').write_text('PRIVATE')
        with self.assertRaises(GateError): self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
    def test_source_symlink_rejected(self):
        a=self.mini()
        (self.source/'shortcut.py').symlink_to(self.source/'main.py')
        with self.assertRaises(GateError): self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
    def test_existing_project_not_reclassified(self):
        other=self.root/'PROJECTS/666CLS'
        other.mkdir(parents=True)
        (other/'CURRENT_POINTER.json').write_text('{"owner":"666CLS"}')
        with self.assertRaises(GateError):self.man.register('666CLS','666CLS','LOCAL_MINI')
        a=self.man.register('666CLS','666CLS','NATIVE_DELEGATED',native_pointer='CURRENT_POINTER.json')
        self.assertEqual(a['record']['write_policy'],'NATIVE_OWNER_ONLY')
        with self.assertRaises(GateError):self.man.save('666CLS',self.source,owner='666CLS',expected_pointer='f'*64)
        h=self.man.handoff('666CLS',desired_action='CODE_SAVE')
        self.assertEqual(h['status'],'PREPARED_NOT_DELIVERED')
    def test_native_owner_proof_mismatch_fails(self):
        other=self.root/'PROJECTS/666CLS'
        other.mkdir(parents=True)
        (other/'CURRENT_POINTER.json').write_text('{"system_id":"666CLS-CORE-001"}')
        with self.assertRaises(GateError):
            self.man.register('666CLS','WRONG-OWNER','NATIVE_DELEGATED',native_pointer='CURRENT_POINTER.json')

    def test_native_root_mismatch_fails(self):
        other=self.root/'PROJECTS/666CLS'
        other.mkdir(parents=True)
        (other/'CURRENT_POINTER.json').write_text('{"system_id":"666CLS-CORE-001","authority":{"root":"PROJECTS/OTHER"}}')
        with self.assertRaises(GateError):
            self.man.register('666CLS','666CLS-CORE-001','NATIVE_DELEGATED',native_pointer='CURRENT_POINTER.json')

    def test_register_duplicate_fails(self):
        self.mini()
        with self.assertRaises(GateError):self.man.register('MINI_01','OTHER','LOCAL_MINI')
    def test_path_traversal_rejected(self):
        for bad in ('../outside.py','/tmp/foo.py','C:/foo.py','.env','src/.git/config'):
            with self.subTest(bad=bad),self.assertRaises(GateError):safe_relative(bad)
    def test_whole_delta_stays_readonly(self):
        a=self.man.whole_delta('a'*40,'b'*40,whole_pointer_present=False)
        self.assertEqual(a['decision'],'READBACK_PENDING')
        self.assertFalse(a['auto_mutation'])
    def test_whole_delta_requires_authority(self):
        a=self.man.whole_delta('a'*40,'b'*40,whole_pointer_present=True)
        self.assertEqual(a['next_authority'],'666 MAIN BRAIN UPDATE')
    def test_native_pointer_change_reported(self):
        other=self.root/'PROJECTS/666CLS'
        other.mkdir(parents=True)
        p=other/'CURRENT_POINTER.json'
        p.write_text('{"owner":"666CLS"}')
        self.man.register('666CLS','666CLS','NATIVE_DELEGATED',native_pointer='CURRENT_POINTER.json')
        p.write_text('{"owner":"666CLS","v":2}')
        self.assertTrue(self.man.status('666CLS')['changed_since_registration'])
    def test_invalid_project_id(self):
        with self.assertRaises(GateError):self.man.register('../bad','OWNER','LOCAL_MINI')
    def test_empty_source_rejected(self):
        a=self.mini()
        (self.source/'main.py').unlink()
        with self.assertRaises(GateError):self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
    def test_unicode_source_preserved(self):
        a=self.mini()
        (self.source/'main.py').write_text('print("💜")\n', encoding='utf8')
        r=self.man.save('MINI_01',self.source,owner='MINI-OWNER',expected_pointer=a['pointer_sha256'])
        self.assertEqual((self.root/'PROJECTS/MINI_01/releases'/r['release']/'src/main.py').read_text(), 'print("💜")\n')

if __name__=='__main__':unittest.main()
