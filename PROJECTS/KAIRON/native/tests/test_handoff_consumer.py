"""666TDI R11 safety and scope regression; execute with PYTHONPATH=source."""
import unittest,pathlib,json,hashlib,importlib.util,builtins
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('tdi_r11',ROOT/'native/handoff_consumer.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class R11Tests(unittest.TestCase):
    def test_identity(self):self.assertEqual(mod.SYSTEM,'666TDI-001')
    def test_findings(self):self.assertEqual(len(mod.REQUIRED),6)
    def test_no_false_blob(self):
        with self.assertRaisesRegex(ValueError,'HANDOFF_BLOB_MISMATCH'):mod.validate_handoff(b'{}')
    def test_scope(self):
        a=json.loads((ROOT/'governance/NATIVE_UPDATE_AUTHORITY.json').read_text('utf-8'))
        self.assertEqual(a['allowed_path_prefix'],'PROJECTS/KAIRON/')
        self.assertFalse(a['foreign_autoactivation'])
        self.assertFalse(a['registered_update_trigger'])
    def test_manifest(self):
        m=json.loads((ROOT/'transfer/SOURCE_MANIFEST.json').read_text('utf-8'))
        self.assertEqual(len(m['source_files']),m['source_file_count'])
        self.assertGreaterEqual(len(m['source_files']),71)
        for p,digest in m['source_files'].items():
            self.assertEqual(hashlib.sha256((ROOT/'source'/p).read_bytes()).hexdigest(),digest,p)
    def test_audio_optional(self):
        a=json.loads((ROOT/'governance/AUDIO_MUSIC_ANALYSIS_OPTIONAL.json').read_text('utf-8'))
        self.assertFalse(a['required_for_systemstart'])
        self.assertFalse(a['required_for_track_creation'])
    def test_clic_handoff_contract(self):
        p=(ROOT/'inbox/CLIC-TO-666TDI-R11-20261122-01.json').read_bytes()
        self.assertEqual(mod.validate_handoff(p)['target_system_id'],mod.SYSTEM)
    def test_missing_numpy(self):
        import sys
        sys.path.insert(0,str(ROOT/'source'))
        try:
            import engine.audio_feedback as audio
            original=builtins.__import__
            def disabled(name,*args,**kwargs):
                if name=='numpy':raise ImportError('disabled')
                return original(name,*args,**kwargs)
            with patch.object(builtins,'__import__',side_effect=disabled):
                with self.assertRaisesRegex(audio.AudioError,'OPTIONAL_AUDIO_DEPENDENCY_MISSING:numpy'):audio._numpy()
        finally:sys.path.pop(0)

    def _remote_fake(self, current_blob=None, current_paths=True, historical_ok=True):
        import base64
        original=(ROOT/'inbox/CLIC-TO-666TDI-R11-20261122-01.json').read_bytes()
        expected_blob=mod.SOURCE_BLOB if current_blob is None else current_blob
        historical_tree=mod.SOURCE_TREE if historical_ok else '0'*40
        base='https://api.github.com/repos/'+mod.SOURCE_REPO
        current_head='f'*40
        current_tree='e'*40
        source_path=mod.PATH
        def mock_json(url):
            if url==base+'/git/ref/heads/'+mod.SOURCE_BRANCH: return {'object':{'sha':current_head}}
            if url==base+'/git/commits/'+current_head: return {'sha':current_head,'tree':{'sha':current_tree}}
            if url==base+'/git/trees/'+current_tree+'?recursive=1':
                return {'truncated':False,'tree':([{'path':source_path,'type':'blob','sha':expected_blob}] if current_paths else [])}
            if url==base+'/git/commits/'+mod.SOURCE_HEAD: return {'sha':mod.SOURCE_HEAD,'tree':{'sha':historical_tree}}
            if url==base+'/git/trees/'+mod.SOURCE_TREE+'?recursive=1':
                return {'truncated':False,'tree':[{'path':source_path,'type':'blob','sha':mod.SOURCE_BLOB}]}
            if url==base+'/git/blobs/'+mod.SOURCE_BLOB:
                return {'encoding':'base64','content':base64.b64encode(original).decode()}
            raise AssertionError('UNEXPECTED_URL:'+url)
        return mock_json
    def test_remote_accepts_newer_source_head_with_identical_blob(self):
        with patch.object(mod,'get_json',side_effect=self._remote_fake()):
            result=mod.verify_remote()
        self.assertEqual(result['current_source_head'],'f'*40)
        self.assertEqual(result['handoff_blob'],mod.SOURCE_BLOB)
    def test_remote_rejects_modified_current_handoff(self):
        with patch.object(mod,'get_json',side_effect=self._remote_fake(current_blob='a'*40)):
            with self.assertRaisesRegex(ValueError,'CURRENT_SOURCE_HANDOFF_CHANGED_OR_MISSING'):
                mod.verify_remote()
    def test_remote_rejects_missing_current_handoff(self):
        with patch.object(mod,'get_json',side_effect=self._remote_fake(current_paths=False)):
            with self.assertRaisesRegex(ValueError,'CURRENT_SOURCE_HANDOFF_CHANGED_OR_MISSING'):
                mod.verify_remote()
    def test_remote_rejects_historical_commit_tree_mismatch(self):
        with patch.object(mod,'get_json',side_effect=self._remote_fake(historical_ok=False)):
            with self.assertRaisesRegex(ValueError,'SOURCE_COMMIT_TREE_MISMATCH'):
                mod.verify_remote()
if __name__=='__main__':unittest.main()
