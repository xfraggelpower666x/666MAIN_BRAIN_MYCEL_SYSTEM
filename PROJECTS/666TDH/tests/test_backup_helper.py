"""Git-Recovery-Sicherung nur auf einer isolierten Minimal-Repository-Fixture."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import verify_and_backup as backup_tool
import test_subfacet_router


@unittest.skipUnless(shutil.which('git'), 'Git für Recovery-Test nicht verfügbar')
class BackupHelperTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.repo=self.root/'repo'
        self.project=self.repo/'PROJECTS/666TDH'
        self.project.parent.mkdir(parents=True)
        f=test_subfacet_router.SubfacetRouterTests('test_root_start_no_child_autoload_and_all_menu_branches')
        f.setUp()
        self.addCleanup(f.doCleanups)
        shutil.copytree(f.root,self.project)
        p=self.project/'runtime/REGISTRY.json'
        reg=json.loads(p.read_text())
        for token in ('FSE','SHACHIVITI'):
            reg['children'][token]['source_identity']='UNRESOLVED_HOLD'
        p.write_text(json.dumps(reg),encoding='utf-8')
        ptr=self.project/'CURRENT_POINTER.json'
        value=json.loads(ptr.read_text())
        value['files']['runtime/REGISTRY.json']=hashlib.sha256(p.read_bytes()).hexdigest()
        ptr.write_text(json.dumps(value),encoding='utf-8')
        (self.repo/'.gitignore').write_text('__pycache__/\n*.pyc\n',encoding='utf-8')
        for path in (ROOT/'tdh.py',ROOT/'runtime/ui/view_model.py',ROOT/'runtime/ui/render_html.py',
                     ROOT/'runtime/facets/lifecycle.py'):
            dst=self.project/path.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,dst)
        for args in (('git','init','-q','-b','666MAIN_BRAIN'),
                     ('git','config','user.name','Synthetic TDH Test'),
                     ('git','config','user.email','synthetic@example.invalid'),
                     ('git','add','.'),('git','commit','-qm','synthetic fixture')):
            subprocess.run(args,cwd=self.repo,check=True,capture_output=True)
        self.scope=patch.object(backup_tool,'PROJECT_ROOT',self.project)
        self.scope.start();self.addCleanup(self.scope.stop)

    def test_zip_preserves_exact_git_head_and_sha256_manifest(self):
        verified=backup_tool.verify()
        out=backup_tool.backup(self.root/'backups',verified=verified)
        self.assertEqual(out['status'],'LOCAL_ZIP_VERIFIED')
        manifest=json.loads(Path(out['manifest']).read_text(encoding='utf-8'))
        with ZipFile(out['zip']) as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(len(manifest['file_sha256']),len([i for i in z.infolist() if not i.is_dir()]))
            self.assertEqual(hashlib.sha256(z.read('PROJECTS/666TDH/CURRENT_POINTER.json')).hexdigest(),
                             manifest['file_sha256']['PROJECTS/666TDH/CURRENT_POINTER.json'])
        self.assertTrue(out['external_vault_not_included'])
        with self.assertRaisesRegex(RuntimeError,'existiert bereits'):
            backup_tool.backup(self.root/'backups',verified=verified)

    def test_dirty_checkout_rejected(self):
        (self.project/'unexpected.txt').write_text('dirty',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'nicht eingecheckte Änderungen'):
            backup_tool.backup(self.root/'backups',verified=backup_tool.verify())

    def test_output_inside_repo_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'nicht innerhalb des Git-Repositories'):
            backup_tool.backup(self.project/'backups',verified=backup_tool.verify())
