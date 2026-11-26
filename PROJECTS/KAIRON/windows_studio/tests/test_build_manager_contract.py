"""Static guardrails that do not claim to execute Windows GUI/NSIS."""
from pathlib import Path
import unittest,json
ROOT=Path(__file__).resolve().parents[1]

class BuildManagerContractTests(unittest.TestCase):
    def test_separate_entrypoints(self):
        self.assertTrue((ROOT/'BUILD_MANAGER.bat').is_file())
        self.assertTrue((ROOT/'STARTEN.bat').is_file())
        self.assertTrue((ROOT/'control-center/main.cjs').is_file())
        target=(ROOT/'electron/main.js').read_text()
        self.assertNotIn("buildkit:action",target)
        self.assertNotIn("setup-control",target)
        self.assertIn("buildkit:action",(ROOT/'control-center/main.cjs').read_text())
    def test_app_settings_are_app_only_and_packaged(self):
        cfg=json.loads((ROOT/'electron/package.json').read_text())
        for file in ['settings-store.cjs','settings-preload.cjs','renderer/**/*']:
            self.assertIn(file,cfg['build']['files'])
        self.assertTrue((ROOT/'electron/renderer/settings.html').exists())
        main=(ROOT/'electron/main.js').read_text()
        self.assertIn("app.getPath('userData')",main)
        self.assertIn("fullscreen:settings.fullscreen",main)
        self.assertIn("settingsStore.save",main)
        self.assertIn("event.senderFrame===settingsWindow.webContents.mainFrame",main)
        self.assertIn("openSettings()",main)
        self.assertIn("input.key==='F11'",main)
    def test_tools_not_reinstalled_automatically(self):
        ps=(ROOT/'tools/bootstrap.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("if(-not(Test-Path $package) -or -not(Test-Path $builder))",ps)
        self.assertIn("Fehlende Electron-Abhaengigkeiten",ps)
        self.assertIn("$mode -notin @('I','U')",ps)
        self.assertIn("winget list --id",ps)
        self.assertIn("winget upgrade --id",ps)
        self.assertIn("-InstallVerifiedRuntime",ps)
    def test_build_targets_and_installer_path_choice_preserved(self):
        pkg=json.loads((ROOT/'electron/package.json').read_text())
        self.assertEqual(pkg['build']['nsis']['allowToChangeInstallationDirectory'],True)
        self.assertIn('portable',pkg['scripts']['build:portable'])
        self.assertIn('nsis',pkg['scripts']['build:setup'])
        self.assertIn('PyInstaller',(ROOT/'tools/pack_backend.py').read_text())

if __name__=='__main__':unittest.main()
