# Windows Runtime Readback Protocol — v1.10.5

Run `VERIFY_WINDOWS_RUNTIME.bat` on the actual Windows 10/11 machine.

The probe performs:

1. governed bootstrap audit;
2. Core version import/readback;
3. Backend import;
4. Tkinter import;
5. Pillow import;
6. real `ChatBackupApp` instantiation from `app/chatbackup_gui.pyw` with the selected bootstrap interpreter;
7. GUI title readback;
8. GUI geometry readback;
9. Browser-Recovery dialog initialization without opening a browser;
10. JSON report creation at `runtime_readback/windows_runtime_readback.json`.

Only a report with `status = WINDOWS_RUNTIME_READBACK_PASS` produced on a real Windows host closes the Windows runtime gate.

A successful Linux/Xvfb run validates probe code only and is not a Windows PASS.


For full host acceptance including a real Share import/export/readback, run `VERIFY_WINDOWS_HOST_ACCEPTANCE.bat`.
