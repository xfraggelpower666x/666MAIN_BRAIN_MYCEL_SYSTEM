param([string]$Action = 'gui')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$logDir = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) '666SOUNDsDESIGn\UniversalBuildkit\logs'
$logFile = Join-Path $logDir 'launcher.log'
try { [void][System.IO.Directory]::CreateDirectory($logDir) } catch {}
function Write-LauncherLog([string]$Message) {
    try { Add-Content -LiteralPath $logFile -Value ("[{0:yyyy-MM-dd HH:mm:ss}] {1}" -f (Get-Date), $Message) -Encoding UTF8 } catch {}
}
if ($Action -eq 'gui') {
    Write-LauncherLog 'GUI start requested.'
    $boot = Join-Path $PSScriptRoot 'tools\cyber-boot.ps1'
    $menu = Join-Path $PSScriptRoot 'tools\menu-gui.ps1'
    if (Test-Path -LiteralPath $boot) {
        try { Write-LauncherLog 'Starting cyber boot.'; & $boot; Write-LauncherLog 'Cyber boot returned.' }
        catch { Write-LauncherLog ("Cyber boot failed: " + ($_ | Out-String)) }
    } else { Write-LauncherLog "Cyber boot script missing: $boot" }
    if (-not (Test-Path -LiteralPath $menu)) {
        $message = "Control Center nicht gefunden:`r`n$menu"
        Write-LauncherLog $message
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show($message,'666 Universal Buildkit','OK','Error') | Out-Null
        exit 2
    }
    $electronMenu=Join-Path $PSScriptRoot 'tools\menu-electron.ps1'
    if(Test-Path -LiteralPath $electronMenu){
        try {
            Write-LauncherLog 'Trying Electron Control Center (existing runtime only).'
            & $electronMenu
            Write-LauncherLog 'Electron Control Center closed normally.'
            exit 0
        } catch {
            Write-LauncherLog ('Electron UI unavailable, keeping PowerShell fallback: ' + ($_ | Out-String))
        }
    }
    try {
        Write-LauncherLog 'Starting Neon Control Center.'
        & $menu
        Write-LauncherLog 'Neon Control Center closed normally.'
        exit 0
    } catch {
        $detail = ($_ | Out-String)
        Write-LauncherLog ("Control Center failed: " + $detail)
        try {
            Add-Type -AssemblyName System.Windows.Forms
            [System.Windows.Forms.MessageBox]::Show("Das Neon-Control-Center konnte nicht gestartet werden.`r`n`r`n$detail`r`nProtokoll: $logFile",'666 Universal Buildkit – Startfehler','OK','Error') | Out-Null
        } catch {}
        exit 3
    }
}
& (Join-Path $PSScriptRoot 'tools\bootstrap.ps1') -Action $Action
if ($LASTEXITCODE -is [int]) { exit $LASTEXITCODE }
