$ErrorActionPreference = 'Stop'

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments, [int[]]$Allowed = @(0))
    & $Executable @Arguments
    if ($LASTEXITCODE -notin $Allowed) {
        throw "$Executable meldet Exitcode $LASTEXITCODE."
    }
}

function Find-Python314 {
    $registryPaths = @(
        'HKCU:\Software\Python\PythonCore\3.14\InstallPath',
        'HKLM:\Software\Python\PythonCore\3.14\InstallPath'
    )
    foreach ($key in $registryPaths) {
        $path = (Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue).ExecutablePath
        if ($path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
            return $path
        }
    }

    $launcher = Get-Command py.exe -CommandType Application -ErrorAction SilentlyContinue
    if ($launcher) {
        $path = & $launcher.Source -3.14 -c 'import sys; print(sys.executable)'
        if ($LASTEXITCODE -eq 0 -and $path -and (Test-Path -LiteralPath $path -PathType Leaf)) {
            return $path
        }
    }
}

try {
    if ((Get-CimInstance Win32_Processor | Select-Object -First 1).Architecture -ne 9) {
        throw 'Der Build-Workflow ist fuer native Windows-x64-Systeme ausgelegt.'
    }

    $winget = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue
    if (-not $winget) {
        Write-Host 'WinGet fehlt. Installiere Microsoft WinGet Client zur Wiederherstellung ...'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Install-PackageProvider -Name NuGet -Force -Scope CurrentUser | Out-Null
        Install-Module -Name Microsoft.WinGet.Client -Scope CurrentUser -Repository PSGallery -Force
        Import-Module Microsoft.WinGet.Client
        Repair-WinGetPackageManager -Force -Latest | Out-Host
        $winget = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue
    }
    if (-not $winget) { throw 'WinGet fehlt weiterhin. Microsoft App Installer installieren und erneut starten.' }

    Invoke-Checked -Executable $winget.Source -Arguments @('--version')
    Invoke-Checked -Executable $winget.Source -Arguments @('source', 'update', '--name', 'winget', '--disable-interactivity')
    try {
        Invoke-Checked -Executable $winget.Source -Arguments @(
            'upgrade', '--exact', '--id', 'Microsoft.AppInstaller', '--source', 'winget',
            '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity'
        ) -Allowed @(0, -1978335189)
    } catch {
        Write-Warning "App Installer konnte nicht aktualisiert werden: $($_.Exception.Message)"
        Invoke-Checked -Executable $winget.Source -Arguments @('--version')
    }

    # "install" aktualisiert ein bereits installiertes Paket, falls ein Upgrade verfuegbar ist.
    Invoke-Checked -Executable $winget.Source -Arguments @(
        'install', '--exact', '--id', 'Python.Python.3.14', '--source', 'winget',
        '--architecture', 'x64', '--silent', '--accept-package-agreements',
        '--accept-source-agreements', '--disable-interactivity'
    ) -Allowed @(0, -1978335189)

    $python = Find-Python314
    if (-not $python) { throw 'Python 3.14 wurde nach der WinGet-Installation nicht gefunden.' }
    Invoke-Checked -Executable $python -Arguments @(
        '-c', 'import struct, sys; assert sys.version_info[:2] == (3, 14) and struct.calcsize(chr(80)) == 8'
    )
    & $python (Join-Path $PSScriptRoot 'build.py') --winget $winget.Source
    exit $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
