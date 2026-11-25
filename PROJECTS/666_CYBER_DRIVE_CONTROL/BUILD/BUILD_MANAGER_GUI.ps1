# Developer-only adapter for Buildkit R01.11.3. Not packaged into Electron.
# The existing BUILD_CONTROL.ps1 remains the single build execution authority.
$ErrorActionPreference='Stop'
if(-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') {
  throw 'Windows WinForms required'
}
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$Root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$controller=Join-Path $PSScriptRoot 'BUILD_CONTROL.ps1'
$form=New-Object System.Windows.Forms.Form
$form.Text='666 CYBER DRIVE CONTROL · UNIVERSAL BUILDKIT R01.11.3'
$form.Size=New-Object System.Drawing.Size(830,590)
$form.MinimumSize=New-Object System.Drawing.Size(760,530)
$form.StartPosition='CenterScreen'
$form.BackColor=[System.Drawing.Color]::FromArgb(13,16,29)
$form.ForeColor=[System.Drawing.Color]::FromArgb(230,239,255)
$form.Font=New-Object System.Drawing.Font('Segoe UI',10)
$header=New-Object System.Windows.Forms.Label
$header.Text='666 CYBER DRIVE · BUILD MANAGER'
$header.Font=New-Object System.Drawing.Font('Segoe UI',20,[System.Drawing.FontStyle]::Bold)
$header.ForeColor=[System.Drawing.Color]::FromArgb(48,224,249)
$header.SetBounds(29,26,755,52)
$form.Controls.Add($header)
$sub=New-Object System.Windows.Forms.Label
$sub.Text='Entwicklerbereich · getrennt von der ausgelieferten Electron-App · vorhandene Build-Pipeline bleibt maßgeblich'
$sub.ForeColor=[System.Drawing.Color]::FromArgb(174,165,214)
$sub.SetBounds(31,88,760,45)
$form.Controls.Add($sub)
$status=New-Object System.Windows.Forms.TextBox
$status.Multiline=$true
$status.ReadOnly=$true
$status.ScrollBars='Vertical'
$status.BackColor=[System.Drawing.Color]::FromArgb(20,27,44)
$status.ForeColor=[System.Drawing.Color]::FromArgb(206,242,248)
$status.SetBounds(29,332,750,195)
$status.Anchor='Bottom,Left,Right,Top'
$form.Controls.Add($status)
function Log([string]$text){$status.AppendText(('[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'),$text)+[Environment]::NewLine)}
function Button([string]$text,[int]$x,[int]$y,[scriptblock]$action){
  $b=New-Object System.Windows.Forms.Button
  $b.Text=$text;$b.SetBounds($x,$y,360,60)
  $b.BackColor=[System.Drawing.Color]::FromArgb(54,38,84)
  $b.ForeColor=[System.Drawing.Color]::FromArgb(243,240,255)
  $b.FlatStyle='Flat';$b.FlatAppearance.BorderColor=[System.Drawing.Color]::FromArgb(190,77,215)
  $b.Add_Click($action);$form.Controls.Add($b)
}
Button '1 · Werkzeug-Status prüfen' 30 155 {
  foreach($cmd in @('node','npm.cmd','py.exe','python.exe','winget','git','pwsh')) {
    $found=Get-Command $cmd -ErrorAction SilentlyContinue
    Log ("$cmd : "+$(if($found){'vorhanden'}else{'nicht verfügbar'}))
  }
}
Button '2 · Original-Buildmenü öffnen' 420 155 {
  Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',('"' + $controller + '"')) -WorkingDirectory $Root
  Log 'Original-Buildcontroller gestartet (eigenes Fenster).'
}
Button '3 · Portable + NSIS über Originalcontroller bauen' 30 236 {
  $answer=[System.Windows.Forms.MessageBox]::Show('Windows-Build jetzt über die ORIGINAL-Buildpipeline starten?','Buildfreigabe','YesNo','Question')
  if($answer -ne 'Yes'){Log 'Build abgebrochen.';return}
  Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-NoExit','-File',('"' + $controller + '"'),'-Action','BuildBoth') -WorkingDirectory $Root
  Log 'Original BuildBoth gestartet. Erfolg erst nach echtem Buildlog prüfen.'
}
Button '4 · Build-Berichte öffnen' 420 236 {
  $reports=Join-Path $Root 'BUILD\REPORTS'
  if(Test-Path $reports){Start-Process -FilePath 'explorer.exe' -ArgumentList ('"' + $reports + '"');Log 'Berichtsordner geöffnet.'}
  else{Log 'Noch kein Berichtsordner vorhanden.'}
}
Log 'Buildkit R01.11.3: kontrollierte Entwickleroberfläche verfügbar.'
Log 'Original-Build-Starter, R18-Quellen und die Electron-App sind getrennt.'
[void]$form.ShowDialog()
$form.Dispose()
