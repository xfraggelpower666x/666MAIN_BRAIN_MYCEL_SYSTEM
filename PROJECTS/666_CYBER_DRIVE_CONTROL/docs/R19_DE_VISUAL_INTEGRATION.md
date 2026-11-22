# R19 D/E visual integration — additive source stage

Source: unchanged original R18 Python modules, directly read from native GitHub commit.
- D uses klrw.ssd.DiskActivitySampler physical device metrics in a separate protocol field 'physical'. Caps/Num/Scroll in Electron are preview-only; threshold derives from the workspace. No device LED write, no false physical-logical matching.
- E uses existing klrw.drive_workspace Workspace and WindowsLogicalDiskSampler volume UUIDs, labels, read/write, tray/overlay preference states. Preferences remain read-only in this stage. User-local writes are not yet exposed.
- Main/preload Electron IPC and build scripts unchanged. Existing R18 tree (186 files) unchanged.
- Files updated: volume_metrics.py, renderer.js, index.html, style.css.
- JavaScript renderer parsed with V8 in the connector runtime. Native Windows runtime/UI/PDH, Python bridge regression and binary build not exercised in this session.
- Next: verified opt-in Workspace update commands in Python subprocess with atomic persistence, then overlay hold/quiet matching R18 and D full mapping persistence.
