import json, pathlib, sys, unittest, tempfile, re, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from diagnose import diagnose

class ToolkitTests(unittest.TestCase):
    def test_default_config_has_schema(self):
        config=json.loads((ROOT/'project.config.json').read_text(encoding='utf-8'))
        self.assertEqual(config['schema'],1)
        self.assertEqual(config['launch_mode'],'python_backend')

    def test_diagnose_readonly(self):
        result=diagnose(ROOT)
        self.assertIn('toolchain',result)
        self.assertIn('git',result['toolchain'])

    def test_boot_assets_and_scaling(self):
        boot=(ROOT/'electron'/'renderer'/'boot.html').read_text(encoding='utf-8')
        self.assertIn('object-fit:contain',boot)
        for dims in [(1920,1080),(1280,720)]:
            data=(ROOT/'electron'/'renderer'/'assets'/f'bootscreen-{dims[0]}x{dims[1]}.webp').read_bytes()
            self.assertTrue(data.startswith(b'RIFF'))
            self.assertEqual(data[8:12],b'WEBP')

    def test_windows_launcher_hides_console_without_changing_execution_policy(self):
        launcher=(ROOT/'STARTEN.bat').read_text(encoding='utf-8')
        vbs=(ROOT/'STARTEN.vbs').read_text(encoding='utf-8')
        self.assertIn('wscript.exe',launcher)
        self.assertIn('STARTEN.vbs',launcher)
        self.assertNotIn('powershell.exe',launcher.lower())
        self.assertIn('shell.Run command, 0, False',vbs)
        self.assertIn('-ExecutionPolicy Bypass',vbs)
        self.assertIn('-NoProfile',vbs)
        self.assertNotIn('Set-ExecutionPolicy',vbs)
        self.assertNotIn('-Scope LocalMachine',vbs)
        self.assertNotIn('-Scope CurrentUser',vbs)

    def test_cyber_boot_timing_eight_seconds(self):
        source=(ROOT/'tools'/'cyber-boot.ps1').read_text(encoding='utf-8-sig')
        duration=int(re.search(r'duration = (\d+)',source).group(1))
        slots=[int(n) for n in re.search(r'milestones = @\(([^)]+)\)',source).group(1).split(',')]
        self.assertEqual(duration,8000)
        self.assertEqual(len(slots),6)
        self.assertEqual(slots,sorted(slots))
        self.assertTrue(all(0 < v < duration for v in slots))
        self.assertGreaterEqual(duration-slots[-1],500)
        self.assertIn('$state.clock.ElapsedMilliseconds',source)
        self.assertIn('if ($ms -ge $state.duration)',source)

    def test_single_surface_boot_uses_one_picturebox(self):
        source=(ROOT/'tools'/'cyber-boot.ps1').read_text(encoding='utf-8-sig')
        self.assertEqual(source.count('[System.Windows.Forms.PictureBox]::new()'),1)
        self.assertIn('$picture.Image = $sourceImage',source)
        self.assertIn('$picture.Add_Paint({',source)
        self.assertNotIn('$form.Add_Paint({',source)
        self.assertNotIn('[System.Windows.Forms.Panel]::new()',source)
        self.assertNotIn('$form.DoubleBuffered = $true',source)

    def test_boot_artwork_is_loaded_once_from_existing_asset_path(self):
        source=(ROOT/'tools'/'cyber-boot.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("Join-Path $PSScriptRoot 'assets\\cyber-boot-artwork.png'",source)
        self.assertEqual(source.count('[System.Drawing.Image]::FromFile($imgPath)'),1)
        self.assertTrue((ROOT/'tools'/'assets'/'cyber-boot-artwork.png').is_file())
        self.assertTrue((ROOT/'tools'/'assets'/'cyber-boot-artwork-original.png').is_file())

    def test_boot_progress_uses_state_and_invalidate_not_legacy_controls(self):
        source=(ROOT/'tools'/'cyber-boot.ps1').read_text(encoding='utf-8-sig')
        self.assertIn('$timer.Interval = 33',source)
        self.assertIn('$timer.Add_Tick({',source)
        self.assertIn('$state.lastPercent = $pct',source)
        self.assertIn('$picture.Invalidate()',source)
        self.assertIn('$state.lastPercent = 100',source)
        for stale in ['$fill.Width','$track.ClientSize','$percentLabel.Text','& $layout']:
            self.assertNotIn(stale,source)

    def test_boot_status_rows_and_ascii_status_codes(self):
        source=(ROOT/'tools'/'cyber-boot.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("$state.status = @('--','--','--','--','--','--')",source)
        self.assertIn("{ 'OK' } else { '!' }",source)
        self.assertIn("'ESC = INTRO UEBERSPRINGEN'",source)
        self.assertIn('$state.log.Add(',source)

    def test_electron_r061_repair_marker_without_newline(self):
        script=(ROOT/'tools'/'electron-runtime-r061.ps1').read_text(encoding='utf-8')
        self.assertIn("[IO.File]::WriteAllText($Marker,'electron.exe',[Text.Encoding]::ASCII)",script)
        self.assertIn('SHASUMS256.txt',script)
        self.assertIn('Get-FileHash',script)

    def test_electron_menu_separate_from_target_app(self):
        self.assertTrue((ROOT/'control-center'/'main.cjs').is_file())
        src=(ROOT/'tools'/'menu-electron.ps1').read_text(encoding='utf-8')
        self.assertIn("$Control=Join-Path $Root 'control-center'",src)
        self.assertIn('& $Exe $Control',src)
        launch=(ROOT/'STARTEN.ps1').read_text(encoding='utf-8-sig')
        self.assertIn('menu-electron.ps1',launch)
        self.assertIn('menu-gui.ps1',launch)

    def test_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)
            cfg=json.loads((ROOT/'project.config.json').read_text(encoding='utf-8'))
            cfg['project_directory']='.'
            cfg['python_entry']='../escape.py'
            (root/'project.config.json').write_text(json.dumps(cfg))
            with self.assertRaises(ValueError):
                diagnose(root)

    def test_electron_and_project_configs_stay_in_sync(self):
        a=json.loads((ROOT/'project.config.json').read_text(encoding='utf-8'))
        b=json.loads((ROOT/'electron'/'config.json').read_text(encoding='utf-8'))
        self.assertEqual(a,b)

    def test_gui_release_label_matches_package_release(self):
        menu=(ROOT/'tools'/'menu-gui.ps1').read_text(encoding='utf-8-sig')
        self.assertIn('R01.11',menu)
        self.assertNotIn('R01.7',menu)


    def test_gui_launcher_always_attempts_menu_after_boot(self):
        source=(ROOT/'STARTEN.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("if ($Action -eq 'gui')",source)
        self.assertIn('& $boot',source)
        self.assertIn('& $menu',source)
        self.assertLess(source.index('& $boot'),source.index('& $menu'))
        self.assertIn('Control Center failed:',source)
        self.assertIn('launcher.log',source)
        self.assertIn('exit 0',source)

    def test_publisher_guardrails(self):
        src=(ROOT/'tools'/'publish-source-to-github.ps1').read_text(encoding='utf-8')
        self.assertIn('Get-FileHash',src)
        self.assertIn('SHA256',src)
        self.assertIn('backup/buildkit-r01-11-pre-publish-',src)
        self.assertIn('git push origin',src)
        self.assertIn('git ls-remote origin',src)
        self.assertIn('git hash-object',src)
        self.assertIn('git config core.autocrlf false',src)
        self.assertNotIn('git push --force',src)
        self.assertIn("$approved -cne 'JA'",src)
        self.assertIn('PROJECTS/666_UNIVERSAL_DEVELOPMENT_BUILDKIT',src)

    def test_control_center_explicit_action_whitelist(self):
        src=(ROOT/'control-center'/'main.cjs').read_text(encoding='utf-8')
        self.assertIn("ipcMain.handle('buildkit:action'",src)
        self.assertIn('actions.has(action)',src)
        self.assertIn('contextIsolation:true',src)
        self.assertIn('sandbox:true',src)
        self.assertIn('nodeIntegration:false',src)

if __name__=='__main__':
    unittest.main()
