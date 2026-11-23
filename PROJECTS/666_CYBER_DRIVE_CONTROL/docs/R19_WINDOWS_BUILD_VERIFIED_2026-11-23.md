# R19 Windows Release Candidate — verified CI artifacts, 2026-11-23

## Canonical source
Repository: xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM
Branch: 666MAIN_BRAIN
Build source commit: 934276e2efc27b75c4d495285b1199f51753dc53
Windows workflow: .github/workflows/cyber-drive-r19-windows.yml
GitHub Actions run: 45243406158
Job: 137933760474
Actions artifact: 14853276212 / cyber-drive-r19-windows-45243406158
Result: completed/success, Windows Server 2022 x64

## Actual Windows gates
- Windows setup-node, setup-python 3.13: PASS
- Original R18 source check: PASS
- R18 Windows pytest: 285 passed, 3 skipped (platform-specific). Not 288/288 on Windows.
- R19 Node contract: 3 passed
- R19 Python feature suite: 3 passed
- Python PyInstaller 6.22.3 produced 666CyberMetrics.exe, --once frozen sidecar smoke: PASS
- electron-builder 25.1.8, Electron 33.4.11: portable and NSIS targets completed
- NSIS package config: oneClick=false, allowToChangeInstallationDirectory=true, perMachine=false
- SHA256 and Windows MZ header independently checked on bytes downloaded from actual CI artifact.

## Individually verified Windows executables
- 666-Cyber-Drive-Control-0.19.1-dev-x64-PORTABLE.exe | 82778080 bytes | SHA256 A773848375BC2A6FDE65E3883212FA8476B1C0A4206658DD88B47207DCBF9EFB
- 666-Cyber-Drive-Control-0.19.1-dev-x64-SETUP.exe | 83005906 bytes | SHA256 B0F8CF012D8F0EC5D8E8BCA3AB85E5FDCDEAFBB114E46AD4338F1A4EF2B2E826

## Prior failure and repair
Run 45243219352 failed with Node -p string quoting on Windows, leading to a wrong winget fallback.
Changed BUILD_CONTROL.ps1 to parse node --version under Windows.
The replacement run 45243406158 succeeded and is the authoritative build proof.

## Non-claims / remaining gates
- A packaged EXE exists and carries a successfully smoke-tested bundled sidecar; the whole Electron GUI has NOT been exercised interactively on a clean Windows desktop.
- NSIS configuration enables destination choice, but the install-directory picker itself and uninstall flow have not been visually exercised.
- Tray icon, overlay, hotplug, full Classic feature parity remain open for native Windows testing.
- package-lock.json and pinned Python dependency constraints are not yet committed. Reproducible dependencies remain PARTIAL.
- Do not present this as a production-certified clean Windows installer, nor as an externally signed release.
- Neither EXE was committed to the Git source repository: distribution is a GitHub Actions artifact.
