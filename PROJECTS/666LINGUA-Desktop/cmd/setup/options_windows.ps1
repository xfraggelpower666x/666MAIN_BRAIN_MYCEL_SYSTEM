$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\666LINGUA'
$old = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
$desktop = [Environment]::GetFolderPath('DesktopDirectory')
$programs = [Environment]::GetFolderPath('Programs')
$options = [ordered]@{
    root = $old.InstallLocation
    previousRoot = $old.InstallLocation
    startLink = if ($programs) { Join-Path $programs '666LINGUA.lnk' } else { '' }
    desktopLink = if ($desktop) { Join-Path $desktop '666LINGUA.lnk' } else { '' }
    startMenu = $false
    desktop = $false
    launch = $true
}
if ($old.StartMenuShortcut) { $options.startLink = $old.StartMenuShortcut }
if ($old.DesktopShortcut) { $options.desktopLink = $old.DesktopShortcut }
if ($options.startLink) { $options.startMenu = !$options.previousRoot -or (Test-Path -LiteralPath $options.startLink) }
if ($options.desktopLink) { $options.desktop = $options.previousRoot -and (Test-Path -LiteralPath $options.desktopLink) }
if (!$options.root) { $options.root = Join-Path $env:LOCALAPPDATA 'Programs\666LINGUA' }
if ($env:LINGUA_SETUP_READ_ONLY -eq '1') {
    $options | ConvertTo-Json -Compress
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()
$form = New-Object System.Windows.Forms.Form
$form.Text = "666LINGUA Setup $env:LINGUA_SETUP_VERSION"
$form.ClientSize = New-Object System.Drawing.Size(590, 300)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.MinimizeBox = $false
$form.TopMost = $true
$setupIcon = $null
if ($env:LINGUA_SETUP_EXE) {
    try {
        $setupIcon = [System.Drawing.Icon]::ExtractAssociatedIcon($env:LINGUA_SETUP_EXE)
        if ($setupIcon) { $form.Icon = $setupIcon }
    } catch {
        # Der Dialog bleibt auch ohne das Symbol benutzbar.
    }
}

function Add-Control($kind, $label, $x, $y, $width, $height) {
    $control = New-Object "System.Windows.Forms.$kind"
    $control.Text = $label
    $control.SetBounds($x, $y, $width, $height)
    $form.Controls.Add($control)
    $control
}
$null = Add-Control Label 'Installationsordner' 20 20 520 24
$folder = Add-Control TextBox $options.root 20 48 435 24
$browse = Add-Control Button 'Durchsuchen…' 465 46 105 28
$browse.Add_Click({
    $picker = New-Object System.Windows.Forms.FolderBrowserDialog
    try {
        $picker.Description = 'Ordner für 666LINGUA auswählen'
        $picker.ShowNewFolderButton = $true
        if ([IO.Directory]::Exists($folder.Text)) { $picker.SelectedPath = $folder.Text }
        if ($picker.ShowDialog($form) -eq 'OK') { $folder.Text = $picker.SelectedPath }
    } finally { $picker.Dispose() }
})
$start = Add-Control CheckBox 'Startmenü-Verknüpfung erstellen' 20 92 550 23
$start.Checked = $options.startMenu
$start.Enabled = [bool]$options.startLink
$desk = Add-Control CheckBox 'Desktop-Verknüpfung erstellen' 20 120 550 23
$desk.Checked = $options.desktop
$desk.Enabled = [bool]$options.desktopLink
$launch = Add-Control CheckBox '666LINGUA nach der Installation starten' 20 148 550 23
$launch.Checked = $true
$null = Add-Control Label "Installation für deinen Windows-Benutzer. Beim Ordnerwechsel bleibt die bisherige Programmdatei im alten Ordner." 20 186 550 48
$install = Add-Control Button 'Installieren' 325 250 115 32
$cancel = Add-Control Button 'Abbrechen' 455 250 115 32
$cancel.DialogResult = 'Cancel'
$form.CancelButton = $cancel
$form.AcceptButton = $install
$install.Add_Click({
    $selected = $folder.Text.Trim()
    try {
        if ($selected -notmatch '^(?:[A-Za-z]:\\|\\\\[^\\]+\\[^\\]+\\)' -or $selected -match '^\\\\[?.]\\') { throw 'Gib einen vollständigen Ordnerpfad ein.' }
        $selected = [IO.Path]::GetFullPath($selected)
        if ($selected.TrimEnd('\') -eq [IO.Path]::GetPathRoot($selected).TrimEnd('\')) { throw 'Wähle einen eigenen Unterordner.' }
        $options.root = $selected
        $options.startMenu = $start.Checked
        $options.desktop = $desk.Checked
        $options.launch = $launch.Checked
        $form.DialogResult = 'OK'
    } catch {
        [void][System.Windows.Forms.MessageBox]::Show($form, $_.Exception.Message, '666LINGUA Setup')
    }
})
try {
    if ($form.ShowDialog() -eq 'OK') { $options | ConvertTo-Json -Compress }
} finally {
    $form.Dispose()
    if ($setupIcon) { $setupIcon.Dispose() }
}
