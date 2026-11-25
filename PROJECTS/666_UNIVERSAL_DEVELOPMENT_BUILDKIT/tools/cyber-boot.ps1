# Copyright 2026 666SOUNDsDESIGn / FRAGGLEPOWER666
# R01.10.3: Bereinigtes HUD-Artwork, Single-PictureBox-Paint, 8-Sekunden-Boot.
# Nur lesende Bootdiagnose; keine Installation oder Projektmutation.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$imgPath = Join-Path $PSScriptRoot 'assets\cyber-boot-artwork.png'
if (-not [System.IO.File]::Exists($imgPath)) { throw "Boot artwork missing: $imgPath" }
# Das Bild wird EINMAL in den Speicher geladen. Es wird nicht im Timer neu gezeichnet.
$sourceImage = [System.Drawing.Image]::FromFile($imgPath)
$Cyan  = [System.Drawing.Color]::FromArgb(48,236,250)
$Pink  = [System.Drawing.Color]::FromArgb(249,73,226)
$White = [System.Drawing.Color]::FromArgb(238,249,255)
$Green = [System.Drawing.Color]::FromArgb(75,247,177)
$Amber = [System.Drawing.Color]::FromArgb(255,188,86)
$Dark  = [System.Drawing.Color]::FromArgb(8,12,30)

$state = @{
    clock = [System.Diagnostics.Stopwatch]::new()
    duration = 8000
    milestones = @(950, 2150, 3350, 4550, 5850, 7200)
    nextStep = 0
    lastPercent = 0
    log = [System.Collections.Generic.List[string]]::new()
    phases = @(
        @{name='INITIALIZING SYSTEM'; check='init'},
        @{name='SCANNING TOOL PATHS'; check='scan'},
        @{name='CHECKING PYTHON'; check='python'},
        @{name='CHECKING GIT'; check='git'},
        @{name='CHECKING NODE / ELECTRON'; check='node'},
        @{name='BUILD ENVIRONMENT SCANNED'; check='done'}
    )
}

$form = [System.Windows.Forms.Form]::new()
$form.Text = '666 UNIVERSAL DEVELOPMENT TOOLS | CYBER BOOT R01.10.3'
$form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
$form.WindowState = [System.Windows.Forms.FormWindowState]::Maximized
$form.BackColor = $Dark
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$form.KeyPreview = $true

# Ein einziges PictureBox zeigt das einmalig geladene Artwork.
# Status, Text und Fortschrittsbalken werden direkt auf derselben Zeichenflaeche gezeichnet.
$picture = [System.Windows.Forms.PictureBox]::new()
$picture.Dock = [System.Windows.Forms.DockStyle]::Fill
$picture.Image = $sourceImage
$picture.SizeMode = [System.Windows.Forms.PictureBoxSizeMode]::Zoom
$picture.BackColor = $Dark
$form.Controls.Add($picture)

$fontTitle = [System.Drawing.Font]::new('Segoe UI', 18, [System.Drawing.FontStyle]::Bold)
$fontRow = [System.Drawing.Font]::new('Segoe UI', 13, [System.Drawing.FontStyle]::Bold)
$fontHint = [System.Drawing.Font]::new('Segoe UI', 10, [System.Drawing.FontStyle]::Regular)
$fontPercent = [System.Drawing.Font]::new('Segoe UI', 15, [System.Drawing.FontStyle]::Bold)
$brushTitle = [System.Drawing.SolidBrush]::new($Cyan)
$brushText = [System.Drawing.SolidBrush]::new($White)
$brushOk = [System.Drawing.SolidBrush]::new($Green)
$brushWarn = [System.Drawing.SolidBrush]::new($Amber)
$brushHint = [System.Drawing.SolidBrush]::new($Cyan)
$brushTrack = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(70,82,105))
$brushPink = [System.Drawing.SolidBrush]::new($Pink)
$state.status = @('--','--','--','--','--','--')
$state.statusOk = @($false,$false,$false,$false,$false,$false)

# Das Bildobjekt bleibt waehrend des gesamten Boots im Speicher. Paint zeichnet
# die Statusdaten direkt auf die vorhandene Bildflaeche; kein Panel/Overlayfenster.
$picture.Add_Paint({
    param($sender, $e)
    $g = $e.Graphics
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
    $iw = [double]$sourceImage.Width; $ih = [double]$sourceImage.Height
    $scale = [Math]::Min($sender.ClientSize.Width/$iw, $sender.ClientSize.Height/$ih)
    if ($scale -le 0) { return }
    $ox = ($sender.ClientSize.Width - $iw*$scale)/2
    $oy = ($sender.ClientSize.Height - $ih*$scale)/2
    $sx = $iw/1672.0*$scale; $sy = $ih/941.0*$scale
    $px = { param($x) [single]($ox + $x*$sx) }.GetNewClosure()
    $py = { param($y) [single]($oy + $y*$sy) }.GetNewClosure()
    $g.DrawString('SYSTEM BOOT / READ-ONLY DIAGNOSTIC',$fontTitle,$brushTitle,(& $px 612),(& $py 378))
    for ($i=0; $i -lt $state.phases.Count; $i++) {
        $y = 426 + ($i*39)
        $g.DrawString($state.phases[$i].name,$fontRow,$brushText,(& $px 640),(& $py $y))
        $brush = if ($state.statusOk[$i]) { $brushOk } elseif ($state.status[$i] -eq '!') { $brushWarn } else { $brushHint }
        $g.DrawString([string]$state.status[$i],$fontRow,$brush,(& $px 1195),(& $py $y))
    }
    $g.DrawString('ESC = INTRO UEBERSPRINGEN',$fontHint,$brushHint,(& $px 620),(& $py 655))
    $barX = & $px 620; $barY = & $py 685; $barW = (& $px 1190)-$barX
    $barH = [Math]::Max(3,[single](10*[Math]::Min($sx,$sy)))
    $g.FillRectangle($brushTrack,$barX,$barY,$barW,$barH)
    $fillW = [single]($barW*[Math]::Max(0,[Math]::Min(100,$state.lastPercent))/100.0)
    if ($fillW -gt 0) { $g.FillRectangle($brushPink,$barX,$barY,$fillW,$barH) }
    $shownPercent = [Math]::Max(0,[Math]::Min(100,[int]$state.lastPercent))
    $g.DrawString("$shownPercent%",$fontPercent,$brushText,(& $px 1200),(& $py 674))
}.GetNewClosure())

$checkPhase = {
    param([string]$Check)
    $findExecutable = {
        param([string[]]$Names)
        foreach ($directory in ([Environment]::GetEnvironmentVariable('PATH') -split ';')) {
            $directory = $directory.Trim('"')
            if ([string]::IsNullOrWhiteSpace($directory)) { continue }
            foreach ($name in $Names) {
                try {
                    $path = [System.IO.Path]::Combine($directory,$name)
                    if ([System.IO.File]::Exists($path)) { return $path }
                } catch { }
            }
        }
        return $null
    }
    switch ($Check) {
        'init' { return @{ ok=$true; info='GUI initialized' } }
        'scan' { return @{ ok=$true; info='Environment PATH inspected' } }
        'python' {
            $value = & $findExecutable @('py.exe','python.exe')
            return @{ ok=[bool]$value; info="Python: $value" }
        }
        'git' {
            $value = & $findExecutable @('git.exe')
            return @{ ok=[bool]$value; info="Git: $value" }
        }
        'node' {
            $value = & $findExecutable @('node.exe')
            $electronPath = Join-Path $PSScriptRoot '..\electron\node_modules\electron'
            return @{ ok=[bool]$value; info="Node: $value; Electron path exists: $(Test-Path -LiteralPath $electronPath)" }
        }
        'done' { return @{ ok=$true; info='Read-only scan completed (not a build readiness certification)' } }
    }
    return @{ ok=$false; info='Unknown boot check' }
}.GetNewClosure()

$timer = [System.Windows.Forms.Timer]::new()
$timer.Interval = 33 # UI thread updates ca. 30 Hz; no full-image redraw.
$timer.Add_Tick({
    try {
        $ms = $state.clock.ElapsedMilliseconds
        $pct = [Math]::Min(100,[int][Math]::Floor($ms*100.0/$state.duration))
        if ($pct -ne $state.lastPercent) {
            $state.lastPercent = $pct
        }
        while ($state.nextStep -lt $state.phases.Count -and $ms -ge $state.milestones[$state.nextStep]) {
            $index = $state.nextStep
            $state.nextStep++
            $phase = $state.phases[$index]
            try {
                $result = & $checkPhase $phase.check
                $state.status[$index] = $(if ($result.ok) { 'OK' } else { '!' })
                $state.statusOk[$index] = [bool]$result.ok
                $state.log.Add("$($phase.name) | $(if ($result.ok) {'ok'} else {'missing'}) | $($result.info)")
            } catch {
                $state.status[$index] = '!'
                $state.statusOk[$index] = $false
                $state.log.Add("$($phase.name) | error | $($_.Exception.Message)")
            }
        }
        $picture.Invalidate()
        if ($ms -ge $state.duration) { $state.lastPercent = 100; $picture.Invalidate(); $timer.Stop(); $form.Close() }
    } catch {
        $state.log.Add("UI timer error: $($_.Exception.Message)")
        $timer.Stop(); $form.Close()
    }
}.GetNewClosure())
$form.Add_Shown({
    $state.clock.Restart()
    $state.lastPercent = 0
    $picture.Invalidate()
    $timer.Start()
}.GetNewClosure())
$form.Add_KeyDown({ if ($_.KeyCode -eq [System.Windows.Forms.Keys]::Escape) { $timer.Stop(); $form.Close() } }.GetNewClosure())

try {
    [void]$form.ShowDialog()
} finally {
    $timer.Stop(); $state.clock.Stop()
    $timer.Dispose(); $form.Dispose(); $sourceImage.Dispose()
    $fontTitle.Dispose(); $fontRow.Dispose(); $fontHint.Dispose(); $fontPercent.Dispose()
    $brushTitle.Dispose(); $brushText.Dispose(); $brushOk.Dispose(); $brushWarn.Dispose(); $brushHint.Dispose(); $brushTrack.Dispose(); $brushPink.Dispose()
}
$logdir = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) '666SOUNDsDESIGn\UniversalBuildkit\logs'
try {
    [void][System.IO.Directory]::CreateDirectory($logdir)
    $state.log | Out-File -LiteralPath (Join-Path $logdir 'last-boot-scan.log') -Encoding UTF8
} catch { Write-Warning "Boot diagnostics could not be saved: $_" }
