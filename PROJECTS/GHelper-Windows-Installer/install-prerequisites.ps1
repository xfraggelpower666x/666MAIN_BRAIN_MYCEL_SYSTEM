$ErrorActionPreference = 'Stop'
$restartRequired = $false

function Invoke-Installer {
    param($Package, [string]$File, [string]$Arguments)
    $path = Join-Path $PSScriptRoot $File
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $Package.sha256) {
        throw "SHA-256 mismatch: $File"
    }
    Write-Host "Installing $File"
    $process = Start-Process -FilePath $path -ArgumentList $Arguments -WorkingDirectory $PSScriptRoot -Wait -PassThru
    $code = $process.ExitCode
    Write-Host "$File exit code: $code"
    if ($code -notin @(0, 3010)) { throw "$File failed with exit code $code." }
    if ($code -eq 3010) { $script:restartRequired = $true }
    return $code
}

function Test-DesktopRuntime {
    param([version]$MinimumVersion)
    $registered = Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\dotnet\Setup\InstalledVersions\x64' -ErrorAction SilentlyContinue
    $roots = @((Join-Path $env:ProgramFiles 'dotnet'), $registered.InstallLocation)
    foreach ($root in $roots) {
        if (-not $root) { continue }
        $missing = $false
        foreach ($framework in @{'Microsoft.WindowsDesktop.App' = 'System.Windows.Forms.dll'; 'Microsoft.NETCore.App' = 'coreclr.dll'}.GetEnumerator()) {
            $installed = Get-ChildItem -LiteralPath (Join-Path $root "shared\$($framework.Key)") -Directory -ErrorAction SilentlyContinue
            $matching = $installed | Where-Object {
                $_.Name -match '^\d+\.\d+\.\d+$' -and
                ([version]$_.Name).Major -eq $MinimumVersion.Major -and
                ([version]$_.Name).Minor -eq $MinimumVersion.Minor -and
                ([version]$_.Name) -ge $MinimumVersion -and
                (Test-Path -LiteralPath (Join-Path $_.FullName $framework.Value) -PathType Leaf)
            }
            if (-not $matching) { $missing = $true }
        }
        if (-not $missing) { return $true }
    }
    return $false
}

function Test-AsusDrivers {
    param([string[]]$DeviceIds, [version]$MinimumVersion)
    $drivers = Get-CimInstance Win32_PnPSignedDriver -Filter "DeviceID LIKE 'ACPI%'"
    foreach ($deviceId in $DeviceIds) {
        $driver = $drivers | Where-Object { $_.DeviceID -eq $deviceId } | Select-Object -First 1
        if (-not $driver -or $driver.DriverVersion -notmatch '^\d+\.\d+\.\d+(\.\d+)?$' -or
            [version]$driver.DriverVersion -lt $MinimumVersion) { return $false }
    }
    return $true
}

try {
    $settings = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'prerequisites.json') | ConvertFrom-Json

    $runtimeVersion = [version]$settings.runtime.version
    if (Test-DesktopRuntime $runtimeVersion) {
        Write-Host "x64 .NET Desktop Runtime $runtimeVersion or newer patch already installed."
    } else {
        $result = Invoke-Installer $settings.runtime 'RuntimeSetup.exe' '/install /quiet /norestart'
        if ($result -ne 3010 -and -not (Test-DesktopRuntime $runtimeVersion)) {
            throw '.NET Desktop Runtime could not be verified after installation.'
        }
    }

    $supportedHardware = @($settings.asus.hardware_ids)
    $deviceIds = @(Get-CimInstance Win32_PnPEntity -Filter 'Present = TRUE' | Where-Object {
        $presentHardware = @($_.HardwareID)
        @($presentHardware | Where-Object { $_ -in $supportedHardware }).Count -gt 0
    } | ForEach-Object { $_.DeviceID })
    $asusVersion = [version]$settings.asus.version
    if ($deviceIds.Count -eq 0) {
        Write-Host 'ASUS: no matching ACPI device. Driver installation skipped.'
    } elseif (Test-AsusDrivers $deviceIds $asusVersion) {
        Write-Host "ASUS System Control Interface $asusVersion or newer already installed."
    } else {
        $result = Invoke-Installer $settings.asus 'AsusSetup.exe' '/SP- /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /RESTARTEXITCODE=3010'
        $verified = $false
        for ($attempt = 0; $attempt -lt 5; $attempt++) {
            if (Test-AsusDrivers $deviceIds $asusVersion) { $verified = $true; break }
            Start-Sleep -Seconds 2
        }
        if (-not $verified -and $result -ne 3010) {
            throw 'ASUS driver version could not be verified. See the ASUS setup log under ProgramData.'
        }
        $script:restartRequired = $true
    }

    $pawnService = 'HKLM:\SYSTEM\CurrentControlSet\Services\PawnIO'
    if (Test-Path -LiteralPath $pawnService) {
        Write-Host 'PawnIO service already registered. Driver installation skipped.'
    } else {
        $result = Invoke-Installer $settings.pawnio 'PawnIO_setup.exe' '-install -silent'
        if ($result -ne 3010 -and -not (Test-Path -LiteralPath $pawnService)) {
            throw 'PawnIO service registration could not be verified.'
        }
    }

    if ($script:restartRequired) { exit 3010 }
    exit 0
} catch {
    Write-Host "Prerequisite installation failed: $($_.Exception.Message)"
    exit 2
}
