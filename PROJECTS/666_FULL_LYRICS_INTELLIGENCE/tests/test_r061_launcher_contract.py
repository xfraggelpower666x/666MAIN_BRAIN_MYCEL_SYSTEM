"""Non-Windows structural checks for the R06.1 Electron start and build contracts.

These are source checks, NOT evidence of Electron running on Windows.
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ElectronLauncherContractTests(unittest.TestCase):
    def test_exact_path_marker_writer(self):
        launch = (ROOT / "tools" / "LAUNCH.ps1").read_text(encoding="utf-8")
        repair = (ROOT / "tools" / "INSTALL_ELECTRON_RUNTIME.ps1").read_text(encoding="utf-8")
        self.assertIn("[System.IO.File]::WriteAllText($marker,$expected,[System.Text.Encoding]::ASCII)", launch)
        self.assertIn("[System.IO.File]::WriteAllText((Join-Path $pkg 'path.txt'), 'electron.exe'", repair)
        self.assertIn("RepairElectronPathMarker", launch)
        self.assertNotIn("Set-Content", repair)

    def test_single_actual_start_entry(self):
        bat = (ROOT / "STARTEN.bat").read_text(encoding="utf-8")
        self.assertIn("tools\\LAUNCH.ps1", bat)
        self.assertTrue((ROOT / "tools" / "LAUNCH.ps1").is_file())

    def test_python_executable_selection_consistent_with_build(self):
        script = (ROOT / "build" / "BUILD_WINDOWS.ps1").read_text(encoding="utf-8")
        self.assertIn("$PythonCmd = if(Get-Command py", script)
        self.assertIn("elseif(Get-Command python", script)
        self.assertNotIn("Require py\n", script)
        self.assertIn("& $PythonCmd @PythonArgs -m PyInstaller --version", script)


if __name__ == "__main__":
    unittest.main()
