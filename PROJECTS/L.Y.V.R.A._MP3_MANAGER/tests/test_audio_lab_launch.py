"""Launcher resolution stays local and never installs dependencies."""
from pathlib import Path
import runpy
import tempfile
import unittest


MODULE = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / 'MP3_Manager.pyw'),
    run_name='audio_lab_launch_test',
)
audio_lab_launch_spec = MODULE['audio_lab_launch_spec']


class AudioLabLaunchTests(unittest.TestCase):
    def test_suno_requires_local_electron_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'Suno-Song-Remaster-main'
            project.mkdir()
            (project / 'package.json').write_text('{}', encoding='utf-8')
            electron = project / 'node_modules/electron/dist/electron.exe'
            electron.parent.mkdir(parents=True)
            electron.touch()

            command, working_directory = audio_lab_launch_spec('suno', [root], 'win32')

            self.assertEqual(command, [str(electron), '.'])
            self.assertEqual(working_directory, project)

    def test_suno_uses_bundled_windows_application(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'Suno-Song-Remaster-main'
            project.mkdir()
            app = project / 'AI Music Remastering.exe'
            app.touch()

            command, working_directory = audio_lab_launch_spec('suno', [root], 'win32')

            self.assertEqual(command, [str(app)])
            self.assertEqual(working_directory, project)

    def test_suno_prefers_bundle_when_source_manifest_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'Suno-Song-Remaster-main'
            project.mkdir()
            (project / 'package.json').write_text('{}', encoding='utf-8')
            app = project / 'AI Music Remastering.exe'
            app.touch()

            command, working_directory = audio_lab_launch_spec('suno', [root], 'win32')

            self.assertEqual(command, [str(app)])
            self.assertEqual(working_directory, project)

    def test_restoration_uses_project_launcher_on_windows(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'Restoration-Lab-main'
            project.mkdir()
            (project / 'STARTEN.bat').touch()

            command, working_directory = audio_lab_launch_spec('restoration', [root], 'win32')

            self.assertEqual(command, ['cmd.exe', '/c', str(project / 'STARTEN.bat')])
            self.assertEqual(working_directory, project)

    def test_restoration_uses_bundled_windows_application(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'Restoration-Lab-main'
            project.mkdir()
            app = project / 'Restoration Lab.exe'
            app.touch()

            command, working_directory = audio_lab_launch_spec('restoration', [root], 'win32')

            self.assertEqual(command, [str(app)])
            self.assertEqual(working_directory, project)

    def test_missing_installation_and_unknown_tool_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                audio_lab_launch_spec('suno', [temp], 'win32')
            with self.assertRaises(ValueError):
                audio_lab_launch_spec('unknown', [temp], 'win32')


if __name__ == '__main__':
    unittest.main()
