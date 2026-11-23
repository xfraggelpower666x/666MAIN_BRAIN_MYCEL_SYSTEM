import importlib.util
from pathlib import Path
import hashlib
import json
import os
import tempfile
import unittest
import zipfile

SOURCE=Path(__file__).resolve().parents[1]/'tools'/'source_readback_guard.py'
spec=importlib.util.spec_from_file_location('guard',SOURCE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

class GuardTests(unittest.TestCase):
    def test_forbidden(self):
        for p in ['output/data.csv','docs/scan.pdf','__pycache__/x.pyc','archive/v1/foo.js','generated_lyrics.md']:
            self.assertTrue(g.forbidden(p),p)
        self.assertFalse(g.forbidden('docs/topics/PSYCHOACOUSTIC_FREQUENCY_MASKING_MATRIX_SOLO_PROMPTS.md'))
        self.assertFalse(g.forbidden('system/core/audit-engine.js'))
    def test_zip_slip(self):
        for p in ['../secrets','/etc/passwd','C:/temp/file','a/../../x','a\\b']:
            self.assertTrue(g.invalid_path(p),p)
    def test_hash_mismatch(self):
        errors=[]
        ret=g.verify_expected({'file.js':'a'*64},{'file.js':'b'*64},errors)
        self.assertEqual(len(ret['mismatched']),1)
    def test_complete_requirements(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'source';root.mkdir()
            for p in ['package.json','system/bootstrap-loader.js','system/config/system-manifest.js','system/core/audit-engine.js','tests/run-tests.js','tools/stem_masking_analyzer.py','tools/sonification_audio_pipeline.py']:
                f=root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('safe')
            manifest=Path(temp)/'manifest.sha'
            manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(root).as_posix()+'\n' for p in sorted(root.rglob('*')) if p.is_file() and p!=manifest))
            r=g.verify(root,manifest)
            self.assertEqual(r['status'],'VERIFIED_SOURCE_ONLY')
            with zipfile.ZipFile(Path(temp)/'test.zip','w') as z:
                for p in root.rglob('*'):
                    if p.is_file() and p.name not in ('test.zip','manifest.sha'):z.write(p,'PROJ/'+p.relative_to(root).as_posix())
            rz=g.verify(Path(temp)/'test.zip',manifest)
            self.assertEqual(rz['status'],'VERIFIED_SOURCE_ONLY')
    def test_zip_extra_file_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); f=root/'a.js'; f.write_text('ok')
            mf=root/'hashes.txt';mf.write_text(hashlib.sha256(f.read_bytes()).hexdigest()+'  a.js\n')
            z=root/'bad.zip'
            with zipfile.ZipFile(z,'w') as archive:
                archive.writestr('a.js','ok');archive.writestr('../evil.js','bad')
            hashes,errors=g.inspect_zip(z,g.parse_hashes(mf))
            self.assertTrue(any('unsafe_member' in x for x in errors))
    def test_symlink_in_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); z=root/'symlink.zip'
            with zipfile.ZipFile(z,'w') as archive:
                info=zipfile.ZipInfo('link.js');info.create_system=3;info.external_attr=(0o120777 << 16)
                archive.writestr(info,'/tmp/evil')
            _,errors=g.inspect_zip(z,{})
            self.assertTrue(any('symlink_member' in x for x in errors))

if __name__=='__main__':unittest.main(verbosity=2)
