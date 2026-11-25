# Neon-Menü für Windows PowerShell 5.1; trennt Darstellung und bestehende Build-Engine.
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Engine = Join-Path $Root 'STARTEN.ps1'
$PowerShellExe = Join-Path $PSHOME 'powershell.exe'
if (-not (Test-Path -LiteralPath $PowerShellExe)) { throw 'Windows PowerShell wurde nicht gefunden.' }
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
function RGB([int]$r,[int]$g,[int]$b) { return [System.Drawing.Color]::FromArgb($r,$g,$b) }
$Black = RGB 9 9 16
$PanelColor = RGB 25 23 37
$Cyan = RGB 53 232 250
$Pink = RGB 255 70 188
$Purple = RGB 178 94 255
$White = RGB 233 244 252
$Muted = RGB 170 165 190

$form = New-Object System.Windows.Forms.Form
$form.Text = '666 UNIVERSAL DEVELOPMENT TOOLS | R01.11'
$form.Size = New-Object System.Drawing.Size(1030,700)
$form.MinimumSize = New-Object System.Drawing.Size(1000,650)
$form.StartPosition = 'CenterScreen'
$form.BackColor = $Black
$form.ForeColor = $White
$form.Font = New-Object System.Drawing.Font('Segoe UI',10)
$form.AutoScaleMode = [System.Windows.Forms.AutoScaleMode]::Dpi

$body = New-Object System.Windows.Forms.Panel
$body.Dock = 'Fill'
$body.BackColor = $Black
$body.AutoScroll = $true
$form.Controls.Add($body)


$title = New-Object System.Windows.Forms.Label
$title.Text = 'DEVELOPMENT CONTROL CENTER'
$title.ForeColor = $Cyan
$title.Font = New-Object System.Drawing.Font('Segoe UI Semibold',18,[System.Drawing.FontStyle]::Bold)
$title.Location = New-Object System.Drawing.Point(25,17)
$title.AutoSize = $true
$body.Controls.Add($title)
$subtitle = New-Object System.Windows.Forms.Label
$subtitle.Text = 'BAT = Einstieg   |   PowerShell = Bedienung   |   Python / Electron = Projekt & Builds'
$subtitle.ForeColor = $Muted
$subtitle.Font = New-Object System.Drawing.Font('Segoe UI',9)
$subtitle.Location = New-Object System.Drawing.Point(29,57)
$subtitle.AutoSize = $true
$body.Controls.Add($subtitle)

$status = New-Object System.Windows.Forms.Label
$status.Location = New-Object System.Drawing.Point(28,414)
$status.Size = New-Object System.Drawing.Size(905,80)
$status.ForeColor = $Muted
$status.Text = 'Bereit. Keine Installation wird automatisch gestartet.'
$body.Controls.Add($status)

function New-ActionButton([string]$Label,[string]$Action,[int]$Index) {
    $column = $Index % 2
    $line = [math]::Floor($Index / 2)
    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Label
    $button.Tag = $Action
    $button.Size = New-Object System.Drawing.Size(447,51)
    $button.Location = New-Object System.Drawing.Point((29 + 465 * $column),(94 + 62 * $line))
    $button.FlatStyle = 'Flat'
    $button.FlatAppearance.BorderSize = 1
    $button.FlatAppearance.BorderColor = $(if ($column -eq 0) {$Cyan} else {$Purple})
    $button.BackColor = $PanelColor
    $button.ForeColor = $White
    $button.Cursor = [System.Windows.Forms.Cursors]::Hand
    $button.TextAlign = [System.Drawing.ContentAlignment]::MiddleLeft
    $button.Padding = New-Object System.Windows.Forms.Padding(14,0,0,0)
    $button.Add_Click({
        $selected = [string]$this.Tag
        $status.Text = "Aktion gestartet: $selected`r`nEin separates PowerShell-Fenster zeigt Eingaben, Ergebnisse und Fehler."
        # Argumente sind ausschließlich feste, interne Aktionsnamen.
        $args = @('-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',('"'+$Engine+'"'),'-Action',$selected)
        try { Start-Process -FilePath $PowerShellExe -ArgumentList $args -WorkingDirectory $Root -ErrorAction Stop | Out-Null }
        catch { [System.Windows.Forms.MessageBox]::Show($_.Exception.Message,'Startfehler','OK','Error') | Out-Null }
    }.GetNewClosure())
    $body.Controls.Add($button)
}
$actions = @(
    @('01    TOOLS SCANNEN','scan'),
    @('02    INSTALL / UPDATE','install'),
    @('03    PYTHON VORBEREITEN','prepare'),
    @('04    PYTHON STARTEN','run-python'),
    @('05    PROJEKT TESTEN','test'),
    @('06    ELECTRON VOLLBILD','run-electron'),
    @('07    PORTABLE EXE BAUEN','portable'),
    @('08    WINDOWS SETUP BAUEN','setup'),
    @('09    ELECTRON RUNTIME PRUEFEN','setup-control')
)
for ($i=0; $i -lt $actions.Count; $i++) { New-ActionButton $actions[$i][0] $actions[$i][1] $i }
$exit = New-Object System.Windows.Forms.Button
$exit.Text = 'SCHLIESSEN'
$exit.Size = New-Object System.Drawing.Size(170,35)
$exit.Location = New-Object System.Drawing.Point(29,509)
$exit.BackColor = $Black
$exit.ForeColor = $Pink
$exit.FlatStyle = 'Flat'
$exit.FlatAppearance.BorderColor = $Pink
$exit.Add_Click({ $form.Close() })
$body.Controls.Add($exit)
$footer = New-Object System.Windows.Forms.Label
$footer.Text = 'R01.11  |  Bestandsprojekt bleibt unverändert  |  Freigaben weiterhin im Build-Fenster'
$footer.ForeColor = $Muted
$footer.Location = New-Object System.Drawing.Point(212,520)
$footer.AutoSize = $true
$body.Controls.Add($footer)

[void]$form.ShowDialog()
