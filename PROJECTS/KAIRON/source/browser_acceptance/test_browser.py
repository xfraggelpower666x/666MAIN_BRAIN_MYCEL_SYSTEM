"""Real Chromium acceptance of KAIRON's existing local daemon.
Run from source: python -m unittest browser_acceptance.test_browser
Install separately: python -m pip install playwright==1.51.0
Then: python -m playwright install chromium
Missing browser/dependency is an explicit failure, not a passing test.
"""
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from engine import daemon_cli, portable


class BrowserAcceptance(unittest.TestCase):
    def test_mandala_forces_and_preset_lifecycle(self):
        from playwright.sync_api import sync_playwright, expect
        with tempfile.TemporaryDirectory() as tmp, patch.object(portable, 'DATA', Path(tmp)):
            server = ThreadingHTTPServer(('127.0.0.1', 0), daemon_cli.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                with sync_playwright() as pw:
                    browser = pw.chromium.launch(headless=True)
                    try:
                        page = browser.new_page()
                        errors = []
                        page.on('pageerror', lambda error: errors.append(str(error)))
                        page.goto(f'http://127.0.0.1:{server.server_port}/')
                        page.locator('[data-device="PC_SUNO_BROWSER"]').click()
                        for key, value in {
                            'motor': 'rolling bass, stable sub, relentless forward motion',
                            'mid': 'acid, directed chaos, shared motif',
                            'voice': 'mantra',
                            'structure': 'drop and break, dynamic contrast',
                            'psychoacoustics': 'orbit, spatial motion',
                            'bpm': '144',
                        }.items():
                            page.locator('#'+key).fill(value)
                        with page.expect_response(lambda r: r.url.endswith('/api/preanalysis')) as response:
                            page.locator('#analyze-button').click()
                        self.assertTrue(response.value.ok)
                        report = response.value.json()
                        expect(page.locator('#evolution-section')).to_be_visible()
                        expect(page.locator('#mandala-view')).to_contain_text('CENTER')
                        expect(page.locator('#mandala-view')).to_contain_text('OUTER')
                        self.assertTrue(report['preanalysis']['musical_forces']['functional_edges'])
                        expect(page.locator('#forces-view')).to_contain_text('CHAOS_TRAJECTORY')
                        page.locator('#preset-id').fill('browser-test')
                        expect(page.locator('#preset-save')).to_be_disabled()
                        with page.expect_response(lambda r: r.url.endswith('/api/preset/read')) as read:
                            page.locator('#preset-read').click()
                        self.assertEqual(read.value.json()['versions'], [])
                        expect(page.locator('#preset-status')).to_contain_text('0 Versionen')
                        expect(page.locator('#preset-save')).to_be_disabled()
                        page.locator('#preset-consent').check()
                        expect(page.locator('#preset-save')).to_be_enabled()
                        with page.expect_response(lambda r: r.url.endswith('/api/preset/save')) as save:
                            page.locator('#preset-save').click()
                        self.assertTrue(save.value.ok)
                        self.assertEqual(save.value.json()['saved']['version'], 1)
                        expect(page.locator('#preset-history')).to_contain_text('Version 1')
                        expect(page.locator('#preset-save')).to_be_disabled()
                        page.locator('#preset-consent').check()
                        with page.expect_response(lambda r: r.url.endswith('/api/preset/save')) as save:
                            page.locator('#preset-save').click()
                        self.assertTrue(save.value.ok)
                        self.assertEqual(save.value.json()['saved']['version'], 2)
                        expect(page.locator('#preset-history')).to_contain_text('Version 2')
                        page.locator('#preset-consent').check()
                        page.locator('#mid').fill('changed after review')
                        expect(page.locator('#evolution-section')).to_be_hidden()
                        self.assertEqual(page.locator('#preset-save').is_visible(), False)
                        self.assertFalse(errors, errors)
                    finally:
                        browser.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main()
