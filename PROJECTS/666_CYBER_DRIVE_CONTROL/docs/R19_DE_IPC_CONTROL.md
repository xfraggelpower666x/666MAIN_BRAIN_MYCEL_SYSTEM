# R19 D/E controlled workspace update

E now exposes editable Tray/Overlay selection per stable R18 Volume ID and overlay layout. Renderer uses narrow preload IPC; Electron main checks command name, allowed target, ID type/size, boolean values and enumerated layout. Python checks existence of target volume in current R18 inventory and calls existing atomic Workspace.save(). The JSON request travels over local child-process stdin and reply over its stdout, with request ID and 5s timeout.

No CapsLock/NumLock/ScrollLock hardware writes. D remains physical DiskActivitySampler visualization with local-only mapping preview, while E remains GUID-backed logical volume PDH. Existing original R18 source 186 files and all batch scripts unchanged.

Validation: new JS main/preload/renderer parsed through V8; existing 288 R18 unit tests passed locally against unchanged ZIP. Windows real IPC / Electron GUI test and new Python bridge test not yet executed, R19 full parity NOT claimed.
