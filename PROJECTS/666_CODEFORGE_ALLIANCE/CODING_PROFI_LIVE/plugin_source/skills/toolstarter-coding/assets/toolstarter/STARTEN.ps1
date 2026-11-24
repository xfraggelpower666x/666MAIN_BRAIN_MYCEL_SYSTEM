# 666SOUNDsDESIGn - FRAGGLEPOWER666
$ErrorActionPreference = 'Stop'
$forward = $args
$starter = Join-Path $PSScriptRoot 'toolstarter.py'
$profileFile = Join-Path $PSScriptRoot 'tools.json'
$index = [Array]::IndexOf($forward, '--profile')
if ($index -ge 0 -and $index + 1 -lt $forward.Count) {
    $profileFile = [IO.Path]::GetFullPath($forward[$index + 1])
}
$profile = Get-Content -LiteralPath $profileFile -Raw -Encoding UTF8 | ConvertFrom-Json
$relativeRoot = if ($profile.project_root) { $profile.project_root } else { '.' }
$root = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $profileFile) $relativeRoot))
$logs = Join-Path $root 'logs'
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$env:Path = @(
    $env:Path
    [Environment]::GetEnvironmentVariable('Path', 'User')
    [Environment]::GetEnvironmentVariable('Path', 'Machine')
    (Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps')
) -join ';'

function Find-Python {
    foreach ($command in @(Get-Command py.exe, python.exe -All -CommandType Application -ErrorAction SilentlyContinue)) {
        if ($command.Source -like '*\Microsoft\WindowsApps\python.exe') { continue }
        $flags = @()
        if ($command.Name -eq 'py.exe') { $flags = @('-3') }
        $resolved = & $command.Source @flags -c 'import sys; print(sys.executable) if sys.version_info >= (3, 10) else sys.exit(1)'
        if ($LASTEXITCODE -eq 0 -and $resolved -and (Test-Path -LiteralPath $resolved -PathType Leaf)) {
            return [string]$resolved
        }
    }
    foreach ($rootKey in @('HKCU:\SOFTWARE\Python\PythonCore', 'HKLM:\SOFTWARE\Python\PythonCore', 'HKLM:\SOFTWARE\WOW6432Node\Python\PythonCore')) {
        foreach ($versionKey in @(Get-ChildItem -LiteralPath $rootKey -ErrorAction SilentlyContinue)) {
            $key = Get-Item -LiteralPath ($versionKey.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if (-not $key -or -not $key.GetValue('')) { continue }
            $candidate = Join-Path ($key.GetValue('')) 'python.exe'
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
            & $candidate -c 'import sys; sys.exit(sys.version_info < (3, 10))'
            if ($LASTEXITCODE -eq 0) { return $candidate }
        }
    }
}

# Die bisherigen direkten Schalter bleiben als Einstieg verwendbar.
if ($forward.Count -gt 0) {
    $leading = $forward[0]
    $rest = @($forward | Select-Object -Skip 1)
    switch ($leading) {
        '--start'   { $forward = @('run', 'start') }
        '--build'   { $forward = @('run', 'build') }
        '--test'    { $forward = @('run', 'test') }
        '--check'   { $forward = @('check') }
        '--repair'  { $forward = @('repair') }
        '--diagnose'{ $forward = @('diagnose') }
        '--portable'{ $forward = @('package', 'portable') }
        '--setup'   { $forward = @('package', 'both') }
    }
    if ($forward[0] -ne $leading) { $forward += $rest }
}
$python = Find-Python
$gui = $forward.Count -eq 0 -or $forward[0] -eq 'gui'
if (-not $python -and ($gui -or $forward[0] -in @('prepare', 'repair', 'run', 'package'))) {
    $log = Join-Path $logs ("bootstrap-{0}-{1}.log" -f (Get-Date -Format 'yyyyMMdd-HHmmss-ffff'), $PID)
    Write-Host "ToolStarter needs CPython. Log: $log"
    $winget = Get-Command winget.exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($winget) {
        & $winget.Source install --id Python.Python.3.13 --exact --source winget --scope user --silent --accept-package-agreements --accept-source-agreements --disable-interactivity |
            Out-File -LiteralPath $log -Encoding UTF8
        $installExit = $LASTEXITCODE
        Add-Content -LiteralPath $log -Value "WinGet exit code: $installExit"
        $python = Find-Python
    } else {
        'WinGet unavailable. Install CPython 3.10 or later for this user.' | Set-Content -LiteralPath $log -Encoding UTF8
    }
}
if (-not $python) { throw "CPython 3.10 or later unavailable. Project logs: $logs" }
if (-not $gui) {
    & $python $starter @forward
    exit $LASTEXITCODE
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object Windows.Forms.Form
$form.Text = '666 TOOLSTARTER'
$form.Width = 920
$form.Height = 610
$form.MinimumSize = New-Object Drawing.Size(640, 400)
$form.StartPosition = 'CenterScreen'
$form.BackColor = [Drawing.Color]::FromArgb(17, 13, 28)
$form.ForeColor = [Drawing.Color]::White
$form.Font = New-Object Drawing.Font('Segoe UI', 10)
$header = New-Object Windows.Forms.Label
$header.Text = "666 TOOLSTARTER  |  $root"
$header.Dock = 'Top'
$header.Height = 42
$header.TextAlign = 'MiddleLeft'
$header.ForeColor = [Drawing.Color]::Cyan
$bar = New-Object Windows.Forms.FlowLayoutPanel
$bar.Dock = 'Top'
$bar.Height = 98
$bar.AutoScroll = $true
$bar.Padding = New-Object Windows.Forms.Padding(8)
$status = New-Object Windows.Forms.Label
$status.Dock = 'Bottom'
$status.Height = 32
$status.TextAlign = 'MiddleLeft'
$status.Text = 'Preparing tool check'
$output = New-Object Windows.Forms.TextBox
$output.Dock = 'Fill'
$output.Multiline = $true
$output.ScrollBars = 'Both'
$output.ReadOnly = $true
$output.BackColor = [Drawing.Color]::FromArgb(24, 20, 39)
$output.ForeColor = [Drawing.Color]::White
$form.Controls.AddRange(@($output, $status, $bar, $header))
$timer = New-Object Windows.Forms.Timer
$timer.Interval = 200
$script:pending = $null

function Quote-Argument([string]$value) {
    $escaped = $value -replace '(\\*)"', '$1$1\"' -replace '(\\+)$', '$1$1'
    return '"' + $escaped + '"'
}

function Start-Operation([string]$label, [string[]]$arguments) {
    if ($script:pending) { return }
    try {
        $info = New-Object Diagnostics.ProcessStartInfo
        $info.FileName = $python
        $items = @($starter, '--profile', $profileFile) + $arguments
        $info.Arguments = ($items | ForEach-Object { Quote-Argument $_ }) -join ' '
        $info.WorkingDirectory = $root
        $info.UseShellExecute = $false
        $info.CreateNoWindow = $true
        $info.RedirectStandardOutput = $true
        $info.RedirectStandardError = $true
        $info.EnvironmentVariables['PYTHONIOENCODING'] = 'utf-8'
        $info.StandardOutputEncoding = [Text.Encoding]::UTF8
        $info.StandardErrorEncoding = [Text.Encoding]::UTF8
        $process = [Diagnostics.Process]::Start($info)
        $script:pending = @{
            Process = $process; Out = $process.StandardOutput.ReadToEndAsync()
            Err = $process.StandardError.ReadToEndAsync(); Label = $label
        }
        $output.Clear()
        $status.Text = "$label running | $logs"
        $timer.Start()
    } catch {
        $status.Text = "$label failed to start"
        $output.AppendText([string]$_)
    }
}

function Add-Operation([string]$label, [string[]]$arguments) {
    $button = New-Object Windows.Forms.Button
    $button.Text = $label
    $button.AutoSize = $true
    $button.MinimumSize = New-Object Drawing.Size(94, 34)
    $button.FlatStyle = 'Flat'
    $button.ForeColor = [Drawing.Color]::FromArgb(255, 139, 231)
    $button.Tag = $arguments
    $button.Add_Click({ param($sender, $eventArgs) Start-Operation $sender.Text $sender.Tag })
    $bar.Controls.Add($button)
}

foreach ($action in $profile.actions.PSObject.Properties) {
    $name = switch ($action.Name) {
        'start' { 'Start application' }
        'build' { 'Build application' }
        'test' { 'Run tests' }
        default { $action.Name }
    }
    Add-Operation $name @('run', $action.Name)
}
if ($profile.package) {
    Add-Operation 'Portable' @('package', 'portable')
    Add-Operation 'Windows Setup' @('package', 'both')
}
Add-Operation 'Tool check / repair' @('repair')
Add-Operation 'Diagnose' @('diagnose')
$open = New-Object Windows.Forms.Button
$open.Text = 'Project logs'
$open.AutoSize = $true
$open.Add_Click({ Invoke-Item -LiteralPath $logs })
$bar.Controls.Add($open)

$timer.Add_Tick({
    $job = $script:pending
    if (-not $job.Process.HasExited -or -not $job.Out.IsCompleted -or -not $job.Err.IsCompleted) { return }
    $timer.Stop()
    $output.Text = $job.Out.Result + $job.Err.Result
    $status.Text = "$($job.Label) | Exit code: $($job.Process.ExitCode) | $logs"
    $job.Process.Dispose()
    $script:pending = $null
})
$form.Add_Shown({ Start-Operation 'Automatic tool check' @('prepare') })
$form.Add_FormClosing({
    param($sender, $eventArgs)
    if ($script:pending) {
        $eventArgs.Cancel = $true
        $status.Text = 'Wait for the active operation to finish.'
    }
})
[void]$form.ShowDialog()
$timer.Dispose()
$form.Dispose()
