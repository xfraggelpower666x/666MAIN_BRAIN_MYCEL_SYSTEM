$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
$ElectronPkg=Join-Path $Root 'electron\node_modules\electron'
$Exe=Join-Path $ElectronPkg 'dist\electron.exe'
$Marker=Join-Path $ElectronPkg 'path.txt'
$Control=Join-Path $Root 'control-center'
if(-not (Test-Path -LiteralPath (Join-Path $Control 'main.cjs'))){throw 'Control Center Quelle fehlt.'}
if(-not (Test-Path -LiteralPath $Exe)){throw 'Electron Runtime nicht vorhanden. PowerShell-Fallback verwenden.'}
if((Get-Item $Exe).Length -lt 1000000){throw 'Electron.exe ist unvollstaendig.'}
$Actual=if(Test-Path $Marker){[IO.File]::ReadAllText($Marker)}else{''}
if($Actual -cne 'electron.exe'){
  # R06.1 fix: only when an existing executable is present, no downloads or upgrades.
  [IO.File]::WriteAllText($Marker,'electron.exe',[Text.Encoding]::ASCII)
}
# Run the existing, local Electron runtime; this is a separate UI entry and does not change target app main.js.
& $Exe $Control
if($LASTEXITCODE -ne 0){throw "Electron Control Center exited: $LASTEXITCODE"}
