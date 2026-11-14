"""Launcher resolution stays local and never installs dependencies."""
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


MODULE = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / 'MP3_Manager.pyw'),
    run_name='audio_lab_launch_test',
)
audio_lab_launch_spec = MODULE['audio_lab_launch_spec']
sunscreen_run_command = MODULE['sunscreen_run_command']


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

    def test_sunocleanser_uses_windows_launcher(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'SunoCleanser-0.2.1'
            project.mkdir()
            launcher = project / 'sunocleanser-gui.bat'
            launcher.touch()

            command, working_directory = audio_lab_launch_spec('sunocleanser', [root], 'win32')

            self.assertEqual(command, ['cmd.exe', '/c', str(launcher)])
            self.assertEqual(working_directory, project)

    def test_sunocleanser_uses_unix_launcher(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'SunoCleanser-0.2.1'
            project.mkdir()
            launcher = project / 'sunocleanser-gui.sh'
            launcher.touch()

            command, working_directory = audio_lab_launch_spec('sunocleanser', [root], 'linux')

            self.assertEqual(command, ['bash', str(launcher)])
            self.assertEqual(working_directory, project)

    def test_mp3gain_requires_gui_and_complete_bridge_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'mp3gain-win-gui-1_3_4-src'
            project.mkdir()
            (project / 'MP3GainGUI.exe').touch()
            (project / 'mp3gain.exe').touch()
            (project / 'resources' / 'app.asar').parent.mkdir(parents=True)
            (project / 'resources' / 'app.asar').touch()
            (project / 'resources' / 'engine' / 'mp3gain-worker.js').parent.mkdir(parents=True)
            (project / 'resources' / 'engine' / 'mp3gain-worker.js').touch()

            command, working_directory = audio_lab_launch_spec('mp3gain', [Path(temp)], 'win32')

            self.assertEqual(command, [str(project / 'MP3GainGUI.exe')])
            self.assertEqual(working_directory, project)

    def test_mp3gain_reports_missing_bridge_and_non_windows(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'mp3gain-win-gui-1_3_4-src'
            project.mkdir()
            (project / 'MP3GainGUI.exe').touch()
            with self.assertRaisesRegex(RuntimeError, 'mp3gain.js-Brücke fehlt'):
                audio_lab_launch_spec('mp3gain', [Path(temp)], 'win32')
            with self.assertRaisesRegex(RuntimeError, 'nur unter Windows'):
                audio_lab_launch_spec('mp3gain', [Path(temp)], 'linux')

    def test_sunscreen_resolves_project_binary_and_system_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'sunscreen-main'
            binary = project / 'target' / 'release' / 'sunscreen'
            binary.parent.mkdir(parents=True)
            binary.touch()

            command, working_directory = audio_lab_launch_spec('sunscreen', [root], 'linux')

            self.assertEqual(command, [str(binary)])
            self.assertEqual(working_directory, project)

        with tempfile.TemporaryDirectory() as temp, patch(
            'shutil.which', return_value='/usr/local/bin/sunscreen'
        ):
            command, working_directory = audio_lab_launch_spec('sunscreen', [Path(temp)], 'linux')
            self.assertEqual(command, ['/usr/local/bin/sunscreen'])
            self.assertEqual(working_directory, Path('/usr/local/bin'))

    def test_sunscreen_command_uses_safe_argument_list_and_supported_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'My Track.mp3'
            source.touch()

            command = sunscreen_run_command('/tools/sunscreen', source)

            self.assertEqual(command, [
                '/tools/sunscreen', str(source), str(source.parent / 'sunscreen'),
                'My Track', '--smooth', '--widen', '--excite', '--match', '--master',
            ])
            with self.assertRaisesRegex(ValueError, 'unterstützt MP3, WAV, FLAC und M4A'):
                sunscreen_run_command('/tools/sunscreen', source.with_suffix('.ogg'))

    def test_missing_installation_and_unknown_tool_fail_explicitly(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                audio_lab_launch_spec('suno', [temp], 'win32')
            with self.assertRaises(ValueError):
                audio_lab_launch_spec('unknown', [temp], 'win32')


if __name__ == '__main__':
    unittest.main()
