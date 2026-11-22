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
        self.assertEqual(a['allowed_path_prefix'],'PROJECTS/666TDI/')
        self.assertFalse(a['foreign_autoactivation'])
        self.assertFalse(a['registered_update_trigger'])
    def test_manifest(self):
        m=json.loads((ROOT/'transfer/SOURCE_MANIFEST.json').read_text('utf-8'))
        self.assertEqual(len(m['source_files']),71)
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
if __name__=='__main__':unittest.main()
