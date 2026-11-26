# R01.10 — Single-Surface Cyber HUD Repair

## R01.10.1 hotfix — timer callback consistency
The first R01.10 package still contained references to the removed legacy controls
`$fill`, `$track`, `$percentLabel`, and `$layout`. The `$layout` call caused the
PowerShell invocation exception shown in the Windows screenshot; the stale progress
control references also prevented the single-surface progress model from being clean.

This hotfix removes those obsolete references. The timer now updates only `$state`
and invalidates the existing PictureBox. The `Shown` handler starts the stopwatch
and initializes the visible percentage to 0.

## Preserved
- Existing R01.9 project and build functions
- 8-second boot duration and milestone schedule
- Single PictureBox / one-time artwork load
- Read-only boot checks
- ESC skip behavior
- Existing PowerShell control-center launch flow

## Acceptance
- Source-level stale-reference scan: PASS
- ZIP integrity and manifest verification: PASS
- Actual Windows PowerShell / WinForms runtime: PENDING user-side readback
