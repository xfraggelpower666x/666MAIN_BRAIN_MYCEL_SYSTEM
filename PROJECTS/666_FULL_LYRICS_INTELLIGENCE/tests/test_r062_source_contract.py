"""Quellbasierte Regressionsgates. Kein Beleg einer echten Windows-GUI-Ausführung."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]

class R062SourceContract(unittest.TestCase):
    def test_packaged_bridge_avoids_asar_cwd(self):
        main=(ROOT/'electron/main.cjs').read_text(encoding='utf-8')
        self.assertIn('cwd:isPackagedEngine()?dir:root',main)
        self.assertIn("path.join(process.resourcesPath,'engine-runtime'",main)

    def test_import_queue_clear_and_post_import_reset(self):
        js=(ROOT/'renderer/app.js').read_text(encoding='utf-8')
        self.assertIn('replace?[]:state.queue',js)
        self.assertIn("$('clearQueue').onclick=()=>enqueue([],{replace:true})",js)
        self.assertIn('enqueue([],{replace:true});notice(`Katalogisierung:',js)

    def test_windows_build_gate_and_optional_modules(self):
        ps=(ROOT/'build/BUILD_WINDOWS.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("$env:OS -ne 'Windows_NT'",ps)
        self.assertIn('--hidden-import pypdf --hidden-import docx',ps)
        self.assertIn('Python bridge binary unexpectedly small',ps)

    def test_navigation_and_error_feedback(self):
        js=(ROOT/'renderer/app.js').read_text(encoding='utf-8')
        self.assertIn("e.setAttribute('aria-current','page')",js)
        self.assertIn("e.removeAttribute('aria-current')",js)
        self.assertIn("flag.textContent=error?'● Fehler':'● Lokal'",js)

if __name__=='__main__': unittest.main()
