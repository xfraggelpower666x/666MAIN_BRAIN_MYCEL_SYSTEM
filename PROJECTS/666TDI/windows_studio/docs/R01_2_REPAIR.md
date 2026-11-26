# R01.2 — PowerShell ExecutionPolicy starter repair

## User error
`STARTEN.ps1 kann nicht geladen werden, da die Ausfuehrung von Skripts auf diesem System deaktiviert ist.` (`UnauthorizedAccess`, exit code 1).

## Verified cause
`STARTEN.bat` invoked `powershell.exe -NoProfile -File` with no process-scoped ExecutionPolicy option. This fails if the local script execution policy disallows `.ps1` files.

## Minimal repair
Added `-ExecutionPolicy Bypass` to the BAT invocation only, preserving `%~dp0`, quoted file paths, argument passing, exit code and pause-on-error. This affects the spawned PowerShell process, not persistent machine/user policies.

## Windows follow-up
1. Extract ZIP to a directory.
2. Double-click `STARTEN.bat`.
3. Choose menu item `1` to scan tools.
4. If policy remains blocked, check effective Group Policy with `Get-ExecutionPolicy -List` and consult device management.

Windows run/portable/setup: READBACK_PENDING.
