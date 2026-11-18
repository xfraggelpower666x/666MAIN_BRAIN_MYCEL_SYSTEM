# Windows PowerShell 5.1 / Nur Lesezugriff; kein automatisches UI-PASS
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$report = [ordered]@{
  schema = 'LYVRA_WINDOWS_HOST_ACCEPTANCE_V1'
  created_utc = [DateTime]::UtcNow.ToString('o')
  tool_version = '2.38'
  operating_system = [Environment]::OSVersion.VersionString
  windows_host = ($env:OS -eq 'Windows_NT')
  monitors = @()
  display_dpi_x = $null
  bundled_ffmpeg = $false
  bundled_ffprobe = $false
  native_gui_start = 'NOT_TESTED_BY_SCRIPT'
  explorer_drag_drop = 'MANUAL_TEST_REQUIRED'
  multi_monitor_window_movement = 'MANUAL_TEST_REQUIRED'
  psychoacoustic_artifact_listening = 'MANUAL_TEST_REQUIRED'
}
try {
  Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
  Add-Type -AssemblyName System.Drawing -ErrorAction Stop
  $screenList = @([System.Windows.Forms.Screen]::AllScreens)
  foreach ($screen in $screenList) {
    $report.monitors += @{ device = $screen.DeviceName; primary = $screen.Primary; width = $screen.Bounds.Width; height = $screen.Bounds.Height; x = $screen.Bounds.X; y = $screen.Bounds.Y }
  }
  $bmp = New-Object System.Drawing.Bitmap(1,1)
  $gfx = [System.Drawing.Graphics]::FromImage($bmp)
  try { $report.display_dpi_x = [double]$gfx.DpiX } finally { $gfx.Dispose(); $bmp.Dispose() }
} catch { $report['monitor_inspection_error'] = $_.Exception.Message }
foreach ($tool in @('ffmpeg','ffprobe')) {
  $file = Join-Path $root ('tools\' + $tool + '.exe')
  $report['bundled_' + $tool] = (Test-Path -LiteralPath $file -PathType Leaf)
}
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
$output = Join-Path $root ("HOST_ABNAHME_WINDOWS_" + $stamp + '.json')
$report | ConvertTo-Json -Depth 8 | Out-File -LiteralPath $output -Encoding UTF8
Write-Host 'HOST_READONLY_DIAGNOSIS_WRITTEN' $output
Write-Host 'MONITORS_FOUND' $report.monitors.Count
Write-Host 'NO_GUI_DRAGDROP_OR_ARTIFACT_PASS_CLAIM'
