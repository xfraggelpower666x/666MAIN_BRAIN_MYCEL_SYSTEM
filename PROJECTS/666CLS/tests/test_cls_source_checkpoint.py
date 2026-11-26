import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from cls_source_checkpoint import verify_source_checkpoint


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name)
        self.src = self.root / 'isolated_candidates/CURES_R08/source'
        self.src.mkdir(parents=True)
        (self.src / 'test.txt').write_text('original', encoding='utf-8')
        sha = hashlib.sha256(b'original').hexdigest()
        (self.src / 'R08_FILE_MANIFEST.json').write_text(json.dumps({
            'schema': '666CURES_R08_LOCAL_FILE_MANIFEST_V1',
            'files_sha256': {'test.txt': sha}}), encoding='utf-8')
        self.ptr = {'source_publication_checkpoint': {
            'id': 'CURES_R08_ISOLATED_FULL_SOURCE_20261125',
            'role': 'IMMUTABLE_CANDIDATE_SOURCE_NOT_NATIVE_RUNTIME',
            'source_root': 'isolated_candidates/CURES_R08/source',
            'receipt': 'isolated_candidates/CURES_R08/PUBLICATION_RECEIPT.json',
            'boundary': 'isolated_candidates/CURES_R08/BOUNDARY.json',
            'cures_owner': '666PFS-CURES-001', 'autoload': False,
            'runtime_promotion': False, 'pfs_hold_preserved': True,
            'foreign_writes': False, 'host_acceptance': False,
            'source_tree_sha': 'a' * 40, 'source_files': 2, 'manifest_bound_files': 1,
            'receipt_blob': 'b' * 40, 'boundary_blob': 'c' * 40}}
        (self.src.parent / 'BOUNDARY.json').write_text(json.dumps({
            'owner': '666CLS-CORE-001', 'current_owner': '666PFS-CURES-001',
            'executable': False, 'autoload': False, 'native_promotion': False,
            'cls_integration': 'REFERENCE_ONLY'}), encoding='utf-8')
        (self.src.parent / 'PUBLICATION_RECEIPT.json').write_text(json.dumps({
            'owner': '666CLS-CORE-001', 'source_git_tree_sha': 'a' * 40,
            'archive_file_entries': 2, 'manifest_bound_files': 1,
            'operational_runtime_imported': False}), encoding='utf-8')

        for filename, field in [('BOUNDARY.json', 'boundary_blob'),
                                ('PUBLICATION_RECEIPT.json', 'receipt_blob')]:
            data = (self.src.parent / filename).read_bytes()
            self.ptr['source_publication_checkpoint'][field] = hashlib.sha1(
                b'blob ' + str(len(data)).encode('ascii') + b'\0' + data
            ).hexdigest()

    def test_valid_source(self):
        self.assertEqual(verify_source_checkpoint(self.root, self.ptr)['verified_files'], 1)

    def test_legacy_pointer(self):
        self.assertEqual(verify_source_checkpoint(self.root, {})['status'], 'NOT_DECLARED')

    def test_mutation_rejected(self):
        (self.src / 'test.txt').write_text('tampered', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_missing_file_rejected(self):
        (self.src / 'test.txt').unlink()
        with self.assertRaises(FileNotFoundError):
            verify_source_checkpoint(self.root, self.ptr)

    def test_traversal_rejected(self):
        m = json.loads((self.src / 'R08_FILE_MANIFEST.json').read_text())
        m['files_sha256'] = {'../BOUNDARY.json': 'f' * 64}
        (self.src / 'R08_FILE_MANIFEST.json').write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, 'path rejected'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_promotion_rejected(self):
        self.ptr['source_publication_checkpoint']['runtime_promotion'] = True
        with self.assertRaisesRegex(ValueError, 'authority/boundary mismatch'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_foreign_owner_rejected(self):
        self.ptr['source_publication_checkpoint']['cures_owner'] = '666CLS-CORE-001'
        with self.assertRaisesRegex(ValueError, 'authority/boundary mismatch'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_manifest_symlink_escape_rejected(self):
        original = self.src / 'R08_FILE_MANIFEST.json'
        external = self.root.parent / (self.root.name + '_outside_manifest.json')
        external.write_bytes(original.read_bytes())
        self.addCleanup(external.unlink)
        original.unlink()
        original.symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'manifest escaped source root'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_missing_manifest_rejected(self):
        (self.src / 'R08_FILE_MANIFEST.json').unlink()
        with self.assertRaises(FileNotFoundError):
            verify_source_checkpoint(self.root, self.ptr)

    def test_symlink_escape_rejected(self):
        external = self.root.parent / (self.root.name + '_outside.txt')
        external.write_text('original')
        self.addCleanup(external.unlink)
        (self.src / 'test.txt').unlink()
        (self.src / 'test.txt').symlink_to(external)
        with self.assertRaisesRegex(ValueError, 'escaped source root'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_receipt_conflict(self):
        p = self.src.parent / 'PUBLICATION_RECEIPT.json'
        d = json.loads(p.read_text()); d['source_git_tree_sha'] = 'c' * 40
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'Git blob mismatch'):
            verify_source_checkpoint(self.root, self.ptr)

    def test_boundary_tampering_rejected(self):
        p = self.src.parent / 'BOUNDARY.json'
        d = json.loads(p.read_text()); d['no_cross_system_merge'] = False
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, 'Git blob mismatch'):
            verify_source_checkpoint(self.root, self.ptr)


if __name__ == '__main__':
    unittest.main()
