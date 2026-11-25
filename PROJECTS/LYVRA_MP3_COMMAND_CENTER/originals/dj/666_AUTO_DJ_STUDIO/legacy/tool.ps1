# ==========================================================
# SCRIPT NAME: 666SOUNDsDESIGn AutoDJ Stream Prep Tool
# VERSION: 1.8.3 BUTTON FIX
# CREATED: 2026-04-20
# MODIFIED: 2026-04-20
#
# PURPOSE:
# - Vollversion fuer Stream- und DJ-Vorbereitung
# - Directory Process + Playlist / Block Builder
# - FFmpeg / FFprobe Auto-Download
# - Backup / Work / Output Struktur
# - Preset-System: STREAM / DJ / CUSTOM
# - MP3 / WAV Output
# - Bitrate / Sample Rate / WAV Bit Depth
# - Loudness + True Peak
# - 666 Metadata System
# - Cover Pool Rotation
# - Conflict Policy Memory
# - Variant Family Distribution fuer gemischtere Playlists
# - Fortschrittsbalken + Live-Log
#
# WICHTIG:
# - ASCII-safe build fuer Windows
# - _BACKUP bleibt unangetastet
# - Standardprofil = STREAM
# ==========================================================

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ----------------------------------------------------------
# SECTION 1 - PATHS
# ----------------------------------------------------------
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ToolsDir   = Join-Path $ScriptRoot "tools"
$FfmpegDir  = Join-Path $ToolsDir "ffmpeg"
$FfmpegExe  = Join-Path $FfmpegDir "bin\ffmpeg.exe"
$FfprobeExe = Join-Path $FfmpegDir "bin\ffprobe.exe"
$MetaFile   = Join-Path $ScriptRoot "metadata.json"
$CoverDir   = Join-Path $ScriptRoot "covers"

# ----------------------------------------------------------
# SECTION 2 - GLOBAL STATE
# ----------------------------------------------------------
$script:ConflictPolicyMode   = "ASK"
$script:ConflictPolicyFolder = $null
$script:ShuffledCoverPool    = @()
$script:CoverIndex           = 0
$script:IsPaused             = $false
$script:AbortRequested       = $false

# ----------------------------------------------------------
# SECTION 3 - DESIGN
# ----------------------------------------------------------
$ColorBackground = [System.Drawing.Color]::FromArgb(46,46,46)
$ColorPanel      = [System.Drawing.Color]::FromArgb(30,30,30)
$ColorPink       = [System.Drawing.Color]::DeepPink
$ColorCyan       = [System.Drawing.Color]::FromArgb(120,220,255)
$ColorGreen      = [System.Drawing.Color]::FromArgb(180,255,180)
$ColorLogBack    = [System.Drawing.Color]::FromArgb(8,8,8)
$ColorLogFore    = [System.Drawing.Color]::FromArgb(160,255,160)
$FontNormal      = New-Object System.Drawing.Font("Consolas", 11)
$FontBold        = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Bold)

# ----------------------------------------------------------
# SECTION 4 - HELPERS
# ----------------------------------------------------------
function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

function Write-Log {
    param([string]$Text)
    $stamp = (Get-Date).ToString("HH:mm:ss")
    $txtLog.AppendText("[" + $stamp + "] " + $Text + "`r`n")
    $txtLog.SelectionStart = $txtLog.TextLength
    $txtLog.ScrollToCaret()
    [System.Windows.Forms.Application]::DoEvents()
}

function Load-MetadataProfile {
    if (Test-Path $MetaFile) {
        try {
            return Get-Content -Path $MetaFile -Raw -Encoding UTF8 | ConvertFrom-Json
        }
        catch {
            Write-Log ("metadata.json unreadable, using fallback defaults.")
        }
    }
    return [PSCustomObject]@{
        artist       = "xXXx_FRAGGLE_xXXx"
        album        = "666SOUUNDsDESIGn 2026"
        year         = "2026"
        genre        = "DARKTECHNO-PSYTRANCE"
        comment      = "xXXx_FRAGGLE_xXXx - FRAGGLEPOWER666 - 666SOUUNDsDESIGn 2026"
        album_artist = "xXXx_FRAGGLE_xXXx"
        composer     = "FRAGGLEPOWER666"
        disc         = "666"
        track        = "666"
    }
}

function Save-MetadataProfile {
    param($Profile)
    $Profile | ConvertTo-Json -Depth 4 | Set-Content -Path $MetaFile -Encoding UTF8
}

function Get-AudioFiles {
    param([string]$Folder)
    $ext = @(".mp3",".wav",".flac",".m4a",".aac",".ogg",".opus",".wma")
    return Get-ChildItem -Path $Folder -File | Where-Object { $ext -contains $_.Extension.ToLower() }
}

function Get-CoverFiles {
    if (-not (Test-Path $CoverDir)) { return @() }
    return Get-ChildItem -Path $CoverDir -File | Where-Object {
        $_.Extension.ToLower() -in @(".jpg",".jpeg",".png",".webp")
    }
}

function Initialize-CoverRotation {
    param([array]$CoverPool)
    if ($CoverPool.Count -gt 0) {
        $script:ShuffledCoverPool = $CoverPool | Sort-Object { Get-Random }
        $script:CoverIndex = 0
    }
    else {
        $script:ShuffledCoverPool = @()
        $script:CoverIndex = 0
    }
}

function Get-NextCover {
    if (-not $script:ShuffledCoverPool -or $script:ShuffledCoverPool.Count -eq 0) {
        return $null
    }
    if ($script:CoverIndex -ge $script:ShuffledCoverPool.Count) {
        $script:ShuffledCoverPool = $script:ShuffledCoverPool | Sort-Object { Get-Random }
        $script:CoverIndex = 0
    }
    $cover = $script:ShuffledCoverPool[$script:CoverIndex]
    $script:CoverIndex++
    return $cover
}

function Clean-Title {
    param([string]$Name)

    $clean = $Name
    $clean = $clean -replace '^[0-9]+[\s\-_\.]*', ''
    $clean = $clean -replace '\s*\(\d+\)', ''
    $clean = $clean -replace '(?i)\bV\d+\b', ''
    $clean = $clean -replace '(?i)\bFINAL\b', ''
    $clean = $clean -replace '(?i)\bMIXDOWN\b', ''
    $clean = $clean -replace '(?i)\bTEMP\b', ''
    $clean = $clean -replace '(?i)\bDRAFT\b', ''
    $clean = $clean -replace '[_\-]+', ' '
    $clean = $clean -replace '\s+', ' '
    $clean = $clean.Trim()

    if ([string]::IsNullOrWhiteSpace($clean)) {
        return $Name
    }
    return $clean
}

function Get-FamilyName {
    param([string]$Name)

    $base = $Name -replace '\s*\(\d+\)', ''
    $base = Clean-Title -Name $base
    return $base.ToLowerInvariant()
}

function Get-SelectedProfile {
    if ($radProfileStream.Checked) { return "STREAM" }
    if ($radProfileDj.Checked)     { return "DJ" }
    return "CUSTOM"
}

function Apply-ProfileSettings {
    $profile = Get-SelectedProfile

    if ($profile -eq "STREAM") {
        $radFormatMp3.Checked = $true
        $cmbBitrate.SelectedItem = "128"
        $cmbSampleRate.SelectedItem = "44100"
        $txtCustomLufs.Text = "-12"
        $txtTruePeak.Text = "-1"
    }
    elseif ($profile -eq "DJ") {
        $radFormatMp3.Checked = $true
        $cmbBitrate.SelectedItem = "320"
        $cmbSampleRate.SelectedItem = "48000"
        $txtCustomLufs.Text = "-11"
        $txtTruePeak.Text = "-1"
    }

    Update-FormatUiState
}

function Get-LufsValue {
    return $txtCustomLufs.Text
}

function Get-TruePeakValue {
    return $txtTruePeak.Text
}

function Update-OverallProgress {
    param([int]$Current,[int]$Total)
    if ($Total -le 0) {
        $prgOverall.Value = 0
        $lblOverall.Text = "Overall: 0%"
        return
    }
    $pct = [int][Math]::Min(100, [Math]::Round(($Current / $Total) * 100))
    $prgOverall.Value = $pct
    $lblOverall.Text = "Overall: " + $pct + "%"
    [System.Windows.Forms.Application]::DoEvents()
}

function Update-FileProgress {
    param([int]$Percent,[string]$Step)
    $safe = [int][Math]::Max(0, [Math]::Min(100, $Percent))
    $prgFile.Value = $safe
    $lblFile.Text = "File: " + $safe + "% | " + $Step
    [System.Windows.Forms.Application]::DoEvents()
}

function Wait-IfPausedOrAbort {
    [System.Windows.Forms.Application]::DoEvents()

    if ($script:AbortRequested) {
        throw "Job aborted by user."
    }

    while ($script:IsPaused) {
        $lblFile.Text = "PAUSED"
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 200
        if ($script:AbortRequested) {
            throw "Job aborted by user."
        }
    }
}

# R02: FFmpeg wird als separater Prozess ueberwacht. ABORT beendet auch
# eine laufende Konvertierung; PAUSE gilt sicher ab der naechsten Datei.
function ConvertTo-WindowsProcessArgument {
    param([AllowEmptyString()][string]$Value)
    if ($Value.Length -gt 0 -and $Value -notmatch '[\s"]') { return $Value }
    $quoted = '"'
    $slashes = 0
    foreach ($ch in $Value.ToCharArray()) {
        if ($ch -eq '\') { $slashes++; continue }
        if ($ch -eq '"') {
            $quoted += ('\' * (2 * $slashes + 1)) + '"'
            $slashes = 0
            continue
        }
        $quoted += ('\' * $slashes) + [string]$ch
        $slashes = 0
    }
    $quoted += ('\' * (2 * $slashes)) + '"'
    return $quoted
}

function Invoke-ControlledFFmpeg {
    param([string[]]$FfmpegArguments)
    Wait-IfPausedOrAbort
    $stderrFile = Join-Path ([System.IO.Path]::GetTempPath()) ('666_autodj_ffmpeg_' + [guid]::NewGuid().ToString('N') + '.stderr.log')
    $stdoutFile = Join-Path ([System.IO.Path]::GetTempPath()) ('666_autodj_ffmpeg_' + [guid]::NewGuid().ToString('N') + '.stdout.log')
    $process = $null
    try {
        # Start-Process (Windows PowerShell 5.1) nimmt einen einzigen
        # Argumentstring. Quoting erhaelt auch Leerzeichen und Anfuehrungszeichen.
        $quotedArgs = @($FfmpegArguments | ForEach-Object { ConvertTo-WindowsProcessArgument -Value ([string]$_) })
        $process = Start-Process -FilePath $FfmpegExe -ArgumentList ($quotedArgs -join ' ') -PassThru -NoNewWindow -RedirectStandardError $stderrFile -RedirectStandardOutput $stdoutFile -ErrorAction Stop
        $pauseWasShown = $false
        while (-not $process.WaitForExit(100)) {
            [System.Windows.Forms.Application]::DoEvents()
            if ($script:AbortRequested) {
                Write-Log 'ABORT: laufenden FFmpeg-Prozess beenden.'
                if (-not $process.HasExited) { $process.Kill() }
                $process.WaitForExit()
                throw 'Job aborted by user.'
            }
            if ($script:IsPaused -and -not $pauseWasShown) {
                Write-Log 'PAUSE vorgemerkt: laufende Datei wird beendet; danach pausiert der Job.'
                $pauseWasShown = $true
            }
            if (-not $script:IsPaused) { $pauseWasShown = $false }
        }
        # Race: Nutzer kann genau zwischen WaitForExit und Rueckgabe abbrechen.
        [System.Windows.Forms.Application]::DoEvents()
        if ($script:AbortRequested) { throw 'Job aborted by user.' }
        $exitCode = $process.ExitCode
        if ($exitCode -ne 0 -and (Test-Path -LiteralPath $stderrFile)) {
            Get-Content -LiteralPath $stderrFile -Tail 15 | ForEach-Object { Write-Log ('FFmpeg: ' + $_) }
        }
        return $exitCode
    }
    finally {
        if ($null -ne $process) {
            if (-not $process.HasExited) {
                try { $process.Kill(); $process.WaitForExit() } catch { }
            }
            $process.Dispose()
        }
        foreach ($tmp in @($stderrFile, $stdoutFile)) {
            if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
        }
    }
}

function Ensure-FFmpeg {
    Ensure-Directory $ToolsDir

    if ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe)) {
        Write-Log ("FFmpeg and FFprobe already present.")
        return $true
    }

    try {
        Write-Log ("Downloading FFmpeg package...")
        $zipPath = Join-Path $ToolsDir "ffmpeg_release_essentials.zip"
        $url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing

        $extractDir = Join-Path $ToolsDir "_ffmpeg_extract"
        if (Test-Path $extractDir) { Remove-Item -Path $extractDir -Recurse -Force }
        Ensure-Directory $extractDir

        Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
        $inner = Get-ChildItem -Path $extractDir -Directory | Select-Object -First 1
        if (-not $inner) { throw "FFmpeg archive could not be unpacked." }

        $newFFmpeg = Join-Path $inner.FullName "bin\ffmpeg.exe"
        $newFFprobe = Join-Path $inner.FullName "bin\ffprobe.exe"
        if (-not ((Test-Path -LiteralPath $newFFmpeg -PathType Leaf) -and (Test-Path -LiteralPath $newFFprobe -PathType Leaf))) {
            throw "Downloaded package missing required executables. Existing tools preserved."
        }
        # Retain existing binaries for manual rollback rather than destructive replacement.
        if (Test-Path -LiteralPath $FfmpegDir) {
            $oldToolsBackup = Join-Path $ToolsDir ("ffmpeg_previous_" + (Get-Date -Format "yyyyMMdd_HHmmss_fff"))
            Move-Item -LiteralPath $FfmpegDir -Destination $oldToolsBackup -ErrorAction Stop
            Write-Log ("Previous FFmpeg tools preserved: $oldToolsBackup")
        }
        try {
            Move-Item -LiteralPath $inner.FullName -Destination $FfmpegDir -ErrorAction Stop
        }
        catch {
            if ($oldToolsBackup -and -not (Test-Path -LiteralPath $FfmpegDir)) {
                Move-Item -LiteralPath $oldToolsBackup -Destination $FfmpegDir -ErrorAction Stop
            }
            throw
        }

        if (Test-Path $zipPath) { Remove-Item -Path $zipPath -Force }
        if (Test-Path $extractDir) { Remove-Item -Path $extractDir -Recurse -Force }

        if ((Test-Path $FfmpegExe) -and (Test-Path $FfprobeExe)) {
            Write-Log ("FFmpeg download complete.")
            return $true
        }

        throw "ffmpeg.exe or ffprobe.exe missing after download."
    }
    catch {
        Write-Log ("FFmpeg download error: $($_.Exception.Message)")
        [System.Windows.Forms.MessageBox]::Show(
            "FFmpeg auto-download failed." + "`r`n`r`n" + $_.Exception.Message,
            "FFmpeg Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        ) | Out-Null
        return $false
    }
}

function Show-MetadataEditor {
    $meta = Load-MetadataProfile

    $editor = New-Object System.Windows.Forms.Form
    $editor.Text = "Standard Metadata"
    $editor.Size = New-Object System.Drawing.Size(540,430)
    $editor.StartPosition = "CenterParent"
    $editor.BackColor = $ColorBackground
    $editor.ForeColor = $ColorGreen

    $items = @(
        @{Label="Artist";       Key="artist";       Value=[string]$meta.artist},
        @{Label="Album";        Key="album";        Value=[string]$meta.album},
        @{Label="Year";         Key="year";         Value=[string]$meta.year},
        @{Label="Genre";        Key="genre";        Value=[string]$meta.genre},
        @{Label="Comment";      Key="comment";      Value=[string]$meta.comment},
        @{Label="Album Artist"; Key="album_artist"; Value=[string]$meta.album_artist},
        @{Label="Composer";     Key="composer";     Value=[string]$meta.composer},
        @{Label="Disc";         Key="disc";         Value=[string]$meta.disc},
        @{Label="Track";        Key="track";        Value=[string]$meta.track}
    )

    $boxes = @{}
    $y = 20
    foreach ($it in $items) {
        $lbl = New-Object System.Windows.Forms.Label
        $lbl.Text = $it.Label
        $lbl.Location = New-Object System.Drawing.Point(20,$y)
        $lbl.Size = New-Object System.Drawing.Size(120,24)
        $lbl.ForeColor = $ColorGreen
        $editor.Controls.Add($lbl)

        $txt = New-Object System.Windows.Forms.TextBox
        $txt.Location = New-Object System.Drawing.Point(150,$y)
        $txt.Size = New-Object System.Drawing.Size(340,24)
        $txt.BackColor = $ColorPanel
        $txt.ForeColor = $ColorGreen
        $txt.Text = $it.Value
        $editor.Controls.Add($txt)

        $boxes[$it.Key] = $txt
        $y += 34
    }

    $btnSaveMeta = New-Object System.Windows.Forms.Button
    $btnSaveMeta.Text = "SAVE METADATA"
    $btnSaveMeta.Location = New-Object System.Drawing.Point(150,340)
    $btnSaveMeta.Size = New-Object System.Drawing.Size(180,36)
    $btnSaveMeta.BackColor = $ColorPink
    $btnSaveMeta.ForeColor = [System.Drawing.Color]::Black

    $btnSaveMeta.Add_Click({
        $newMeta = [PSCustomObject]@{
            artist       = $boxes["artist"].Text
            album        = $boxes["album"].Text
            year         = $boxes["year"].Text
            genre        = $boxes["genre"].Text
            comment      = $boxes["comment"].Text
            album_artist = $boxes["album_artist"].Text
            composer     = $boxes["composer"].Text
            disc         = $boxes["disc"].Text
            track        = $boxes["track"].Text
        }
        Save-MetadataProfile $newMeta
        [System.Windows.Forms.MessageBox]::Show("Metadata saved.","OK",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
        $editor.Close()
    })

    $editor.Controls.Add($btnSaveMeta)
    $editor.ShowDialog() | Out-Null
}

function Show-ConflictDialog {
    $dialog = New-Object System.Windows.Forms.Form
    $dialog.Text = "Output Conflict"
    $dialog.Size = New-Object System.Drawing.Size(430,250)
    $dialog.StartPosition = "CenterParent"
    $dialog.BackColor = $ColorBackground
    $dialog.ForeColor = $ColorGreen

    $lbl = New-Object System.Windows.Forms.Label
    $lbl.Text = "Target file already exists. Choose conflict policy:"
    $lbl.Location = New-Object System.Drawing.Point(20,20)
    $lbl.Size = New-Object System.Drawing.Size(380,40)
    $dialog.Controls.Add($lbl)

    $script:DialogResultMode = "THIS"

    $btnThis = New-Object System.Windows.Forms.Button
    $btnThis.Text = "OVERWRITE THIS FILE"
    $btnThis.Location = New-Object System.Drawing.Point(20,70)
    $btnThis.Size = New-Object System.Drawing.Size(170,36)
    $btnThis.BackColor = $ColorCyan
    $btnThis.ForeColor = [System.Drawing.Color]::Black
    $btnThis.Add_Click({ $script:DialogResultMode = "THIS"; $dialog.Close() })
    $dialog.Controls.Add($btnThis)

    $btnAll = New-Object System.Windows.Forms.Button
    $btnAll.Text = "OVERWRITE ALL"
    $btnAll.Location = New-Object System.Drawing.Point(210,70)
    $btnAll.Size = New-Object System.Drawing.Size(170,36)
    $btnAll.BackColor = $ColorPink
    $btnAll.ForeColor = [System.Drawing.Color]::Black
    $btnAll.Add_Click({ $script:DialogResultMode = "ALL"; $dialog.Close() })
    $dialog.Controls.Add($btnAll)

    $btnFolder = New-Object System.Windows.Forms.Button
    $btnFolder.Text = "NEW OUTPUT FOR ALL"
    $btnFolder.Location = New-Object System.Drawing.Point(20,120)
    $btnFolder.Size = New-Object System.Drawing.Size(170,36)
    $btnFolder.BackColor = $ColorCyan
    $btnFolder.ForeColor = [System.Drawing.Color]::Black
    $btnFolder.Add_Click({ $script:DialogResultMode = "FOLDER"; $dialog.Close() })
    $dialog.Controls.Add($btnFolder)

    $btnAbort = New-Object System.Windows.Forms.Button
    $btnAbort.Text = "ABORT JOB"
    $btnAbort.Location = New-Object System.Drawing.Point(210,120)
    $btnAbort.Size = New-Object System.Drawing.Size(170,36)
    $btnAbort.BackColor = $ColorPink
    $btnAbort.ForeColor = [System.Drawing.Color]::Black
    $btnAbort.Add_Click({ $script:DialogResultMode = "ABORT"; $dialog.Close() })
    $dialog.Controls.Add($btnAbort)

    $dialog.ShowDialog() | Out-Null
    return $script:DialogResultMode
}

function Resolve-OutputTarget {
    param([string]$DefaultTargetPath)

    if ($script:ConflictPolicyMode -eq "OVERWRITE_ALL") {
        return [PSCustomObject]@{ Mode="OVERWRITE"; Folder=$null }
    }
    if ($script:ConflictPolicyMode -eq "NEW_OUTPUT_ALL") {
        return [PSCustomObject]@{ Mode="NEWFOLDER"; Folder=$script:ConflictPolicyFolder }
    }
    if ($script:ConflictPolicyMode -eq "ABORT_JOB") {
        return [PSCustomObject]@{ Mode="ABORT"; Folder=$null }
    }

    if (-not (Test-Path $DefaultTargetPath)) {
        return [PSCustomObject]@{ Mode="WRITE"; Folder=$null }
    }

    $choice = Show-ConflictDialog
    switch ($choice) {
        "THIS" {
            return [PSCustomObject]@{ Mode="OVERWRITE"; Folder=$null }
        }
        "ALL" {
            $script:ConflictPolicyMode = "OVERWRITE_ALL"
            return [PSCustomObject]@{ Mode="OVERWRITE"; Folder=$null }
        }
        "FOLDER" {
            $folderDialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $folderDialog.Description = "Choose new output folder for all conflicts"
            if ($folderDialog.ShowDialog() -eq "OK") {
                $script:ConflictPolicyMode = "NEW_OUTPUT_ALL"
                $script:ConflictPolicyFolder = $folderDialog.SelectedPath
                Ensure-Directory $script:ConflictPolicyFolder
                return [PSCustomObject]@{ Mode="NEWFOLDER"; Folder=$script:ConflictPolicyFolder }
            }
            else {
                return [PSCustomObject]@{ Mode="SKIP"; Folder=$null }
            }
        }
        "ABORT" {
            $script:ConflictPolicyMode = "ABORT_JOB"
            return [PSCustomObject]@{ Mode="ABORT"; Folder=$null }
        }
        default {
            return [PSCustomObject]@{ Mode="SKIP"; Folder=$null }
        }
    }
}

function Get-AudioDurationSeconds {
    param([string]$Path)
    try {
        $probeOutput = & $FfprobeExe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $Path 2>$null
        if ($LASTEXITCODE -eq 0 -and $probeOutput) {
            $value = [double]::Parse(($probeOutput | Select-Object -First 1), [System.Globalization.CultureInfo]::InvariantCulture)
            if ($value -gt 0 -and $value -lt 86400) {
                return [int][Math]::Round($value)
            }
        }
    }
    catch { }
    return 0
}

function Update-FormatUiState {
    if ($radFormatMp3.Checked) {
        $cmbBitrate.Enabled = $true
        $cmbWavBitDepth.Enabled = $false
    }
    else {
        $cmbBitrate.Enabled = $false
        $cmbWavBitDepth.Enabled = $true
    }
}

function Get-CheckboxState {
    param([object]$Control)
    try {
        if ($null -eq $Control) { return $false }
        if ($Control -is [System.Windows.Forms.CheckBox]) { return [bool]$Control.Checked }
        if ($Control.PSObject.Properties.Name -contains "Checked") { return [bool]$Control.Checked }
    }
    catch { }
    return $false
}

function Get-ControlTextSafe {
    param([object]$Control, [string]$Fallback = "")
    try {
        if ($null -eq $Control) { return $Fallback }
        if ($Control -is [string]) { return $Control }
        if ($Control.PSObject.Properties.Name -contains "Text") { return [string]$Control.Text }
    }
    catch { }
    return $Fallback
}

function Write-CriticalError {
    param([string]$Message)
    Write-Log ("CRITICAL ERROR: " + $Message)
}

function Get-RelativeSafePath {
    param(
        [string]$BaseFolder,
        [string]$FullPath
    )
    $relative = $FullPath.Substring($BaseFolder.Length).TrimStart('\')
    return $relative
}

function Run-FullBackupPhase {
    param(
        [string]$InputFolder,
        [array]$AudioFiles,
        [string]$BackupDir
    )

    Ensure-Directory $BackupDir
    Write-Log ("BACKUP PHASE START")
    Write-Log ("Backup target: $BackupDir")
    Write-Log ("Backup files total: $($AudioFiles.Count)")

    Update-OverallProgress -Current 0 -Total $AudioFiles.Count
    $i = 0

    foreach ($file in $AudioFiles) {
        Wait-IfPausedOrAbort
        $i++
        Update-OverallProgress -Current $i -Total $AudioFiles.Count
        Update-FileProgress -Percent 0 -Step ("Backup " + $file.Name)

        $relative = Get-RelativeSafePath -BaseFolder $InputFolder -FullPath $file.FullName
        $backupTarget = Join-Path $BackupDir $relative
        $backupTargetDir = Split-Path $backupTarget -Parent
        Ensure-Directory $backupTargetDir

        if (-not (Test-Path -LiteralPath $backupTarget -PathType Leaf)) {
            Copy-Item -LiteralPath $file.FullName -Destination $backupTarget -ErrorAction Stop
            Write-Log ("Backup created: $relative")
        }
        else {
            Write-Log ("Backup already exists; verifying: $relative")
        }

        # Per-file content verification. Never silently replace an older backup.
        $sourceHash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256 -ErrorAction Stop).Hash
        $backupHash = (Get-FileHash -LiteralPath $backupTarget -Algorithm SHA256 -ErrorAction Stop).Hash
        if ($sourceHash -ne $backupHash) {
            throw ("Backup hash mismatch for $relative. Existing backup was preserved. Resolve manually before processing.")
        }
    }

    Write-Log ("Backup SHA256 verification passed: $($AudioFiles.Count) files")

    Update-FileProgress -Percent 100 -Step "Backup complete"
    Write-Log ("BACKUP PHASE END")
    Write-Log ("----------------------------------------")
}

function Get-OutputExtension {
    if ($radFormatMp3.Checked) { return ".mp3" }
    return ".wav"
}

function Build-FfmpegArgs {
    param(
        [string]$InputPath,
        [string]$WorkTarget,
        [string]$BaseTitle,
        $Meta,
        $SelectedCover
    )

    $args = @("-y", "-i", $InputPath)

    if ($chkCover.Checked -and $SelectedCover -ne $null -and $chkReplaceCover.Checked) {
        $args += @("-i", $SelectedCover.FullName)
        $args += @("-map", "0:a", "-map", "1:v")
        $args += @("-c:v", "mjpeg")
        $args += @("-id3v2_version", "3")
        $args += @("-metadata:s:v", "title=Cover")
        $args += @("-metadata:s:v", "comment=Front Cover")
    }
    else {
        if ($chkReplaceCover.Checked) {
            $args += @("-map", "0:a")
        }
    }

    if ($chkNormalize.Checked) {
        $args += @("-filter:a", "loudnorm=I=$(Get-LufsValue):TP=$(Get-TruePeakValue):LRA=7")
    }

    $sampleRate = [string]$cmbSampleRate.SelectedItem
    if (-not [string]::IsNullOrWhiteSpace($sampleRate)) {
        $args += @("-ar", $sampleRate)
    }

    if ($radFormatMp3.Checked) {
        $bitrate = [string]$cmbBitrate.SelectedItem
        if ([string]::IsNullOrWhiteSpace($bitrate)) { $bitrate = "128" }
        $args += @("-c:a", "libmp3lame", "-b:a", ($bitrate + "k"))
    }
    else {
        $depth = [string]$cmbWavBitDepth.SelectedItem
        switch ($depth) {
            "24" { $args += @("-c:a", "pcm_s24le") }
            "32" { $args += @("-c:a", "pcm_s32le") }
            default { $args += @("-c:a", "pcm_s16le") }
        }
    }

    if ($chkMetadata.Checked) {
        $args += @("-metadata", "title=$BaseTitle")
        $args += @("-metadata", "artist=$($Meta.artist)")
        $args += @("-metadata", "album=$($Meta.album)")
        $args += @("-metadata", "date=$($Meta.year)")
        $args += @("-metadata", "genre=$($Meta.genre)")
        $args += @("-metadata", "comment=$($Meta.comment)")
        $args += @("-metadata", "album_artist=$($Meta.album_artist)")
        $args += @("-metadata", "composer=$($Meta.composer)")
        $args += @("-metadata", "disc=$($Meta.disc)")
        $args += @("-metadata", "track=$($Meta.track)")
    }

    $args += @($WorkTarget)
    return ,$args
}

function Run-DirectoryProcess {
    param([string]$InputFolder)

    $audioFiles = Get-RecursiveAudioFiles -Folder $InputFolder
    if (-not $audioFiles -or $audioFiles.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("No supported audio files found.", "No Audio Files",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
        return
    }

    $meta = Load-MetadataProfile
    $coverPool = Get-CoverFiles
    Initialize-CoverRotation -CoverPool $coverPool

    $backupDir = Join-Path $InputFolder "_BACKUP"
    $workDir   = Join-Path $InputFolder "_WORK"
    $outputDir = Join-Path $InputFolder "_OUTPUT"
    Ensure-Directory $backupDir
    Ensure-Directory $workDir
    Ensure-Directory $outputDir

    Write-Log "----------------------------------------"
    Write-Log ("DIRECTORY PROCESS START")
    Write-Log ("Backup mode: FULL BACKUP FIRST")
    Write-Log ("Files found: $($audioFiles.Count)")
    Write-Log ("Profile: $(Get-SelectedProfile)")
    Write-Log ("Format: $(if($radFormatMp3.Checked){'MP3'}else{'WAV'})")
    Write-Log ("Sample Rate: $([string]$cmbSampleRate.SelectedItem)")

    # Safety gate: never process or overwrite audio before a verified backup exists.
    Run-FullBackupPhase -InputFolder $InputFolder -AudioFiles $audioFiles -BackupDir $backupDir

    $script:ConflictPolicyMode = "ASK"
    $script:ConflictPolicyFolder = $null

    Update-OverallProgress -Current 0 -Total $audioFiles.Count
    $count = 0

    foreach ($file in $audioFiles) {
        Wait-IfPausedOrAbort
        $count++
        Update-OverallProgress -Current $count -Total $audioFiles.Count

        try {
            Update-FileProgress -Percent 5 -Step "Backup"
            Write-Log ("Processing: $($file.Name)")

            $baseTitle = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
            if ($chkCleanTitle.Checked) {
                $baseTitle = Clean-Title -Name $baseTitle
            }

            $ext = Get-OutputExtension
            $workTarget = Join-Path $workDir ($baseTitle + $ext)
            if (Test-Path $workTarget) { Remove-Item -Path $workTarget -Force }

            $defaultFinal = Join-Path $InputFolder ($baseTitle + $ext)
            $sameOriginal = ($defaultFinal -eq $file.FullName)
            $finalTarget = $defaultFinal

            if ((Test-Path $defaultFinal) -and (-not $sameOriginal)) {
                $decision = Resolve-OutputTarget -DefaultTargetPath $defaultFinal

                if ($decision.Mode -eq "ABORT") {
                    Write-Log ("Job aborted by conflict policy.")
                    break
                }
                elseif ($decision.Mode -eq "SKIP") {
                    Write-Log ("Skipped because of output conflict: $($file.Name)")
                    continue
                }
                elseif ($decision.Mode -eq "NEWFOLDER") {
                    $finalTarget = Join-Path $decision.Folder ($baseTitle + $ext)
                }
            }

            $selectedCover = $null
            if ($chkCover.Checked -and $coverPool.Count -gt 0) {
                $selectedCover = Get-NextCover
            }

            Update-FileProgress -Percent 30 -Step "FFmpeg"

            $args = Build-FfmpegArgs -InputPath $file.FullName -WorkTarget $workTarget -BaseTitle $baseTitle -Meta $meta -SelectedCover $selectedCover

            Write-Log ("FFmpeg input: $($file.FullName)")
            Write-Log ("FFmpeg output: $workTarget")

            $ffmpegExit = Invoke-ControlledFFmpeg -FfmpegArguments $args
            if ($ffmpegExit -ne 0 -or -not (Test-Path $workTarget)) {
                throw ("FFmpeg processing failed. ExitCode=" + $ffmpegExit)
            }

            Update-FileProgress -Percent 80 -Step "Write Output"
            Copy-Item -Path $workTarget -Destination $finalTarget -Force

            if ((Get-CheckboxState $chkPeakSafety)) {
                $peakInfo = Test-PeakSafety -Path $finalTarget
                if ($peakInfo.Found) {
                    Write-Log ("Peak check: $baseTitle | max_volume=$($peakInfo.MaxVolume) dB")
                    if (-not $peakInfo.Safe) {
                        Write-Log ("WARNING: Possible clipping risk detected for $baseTitle")
                    }
                }
            }

            Update-FileProgress -Percent 100 -Step "Done"
            Write-Log ("Done: $baseTitle")
        }
        catch {
            if ($script:AbortRequested) {
                if (Test-Path -LiteralPath $workTarget) { Remove-Item -LiteralPath $workTarget -Force -ErrorAction SilentlyContinue }
                throw 'Job aborted by user.'
            }
            Write-Log ("ERROR with $($file.Name): $($_.Exception.Message)")
            Update-FileProgress -Percent 0 -Step "Error"
        }
    }

    Wait-IfPausedOrAbort
    Update-FileProgress -Percent 100 -Step "Job Complete"
    Write-Log ("DIRECTORY PROCESS END")
    Write-Log "----------------------------------------"
    [System.Windows.Forms.MessageBox]::Show("Directory process complete.", "Done",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
}

function Build-VariantCatalog {
    param([array]$AudioFiles)

    $groups = @{}
    foreach ($f in $AudioFiles) {
        $name = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        $family = Get-FamilyName -Name $name

        if (-not $groups.ContainsKey($family)) {
            $groups[$family] = @()
        }

        $groups[$family] += [PSCustomObject]@{
            File = $f
            Title = $name
            Family = $family
            Artist = (Get-ArtistName -Name $name)
            Energy = (Get-EnergyBucket -Name $name)
            Duration = (Get-AudioDurationSeconds -Path $f.FullName)
        }
    }

    $families = @()
    foreach ($key in $groups.Keys) {
        $members = $groups[$key]
        $members = $members | Sort-Object { Get-Random }
        $families += [PSCustomObject]@{
            Family = $key
            Members = $members
        }
    }

    return $families | Sort-Object { Get-Random }
}

function Build-BalancedPlaylistBlocks {
    param(
        [array]$Families,
        [string]$SplitMode,
        [int]$TargetMinutes,
        [int]$TargetTracks
    )

    # Determine approximate block count
    $totalSeconds = 0
    $totalTracks = 0
    foreach ($fam in $Families) {
        foreach ($m in $fam.Members) {
            $totalSeconds += $m.Duration
            $totalTracks++
        }
    }

    $blockCount = 1
    if ($SplitMode -eq "MINUTES") {
        if ($TargetMinutes -gt 0) {
            $blockCount = [Math]::Max(1, [int][Math]::Ceiling($totalSeconds / ($TargetMinutes * 60)))
        }
    }
    elseif ($SplitMode -eq "TRACKS") {
        if ($TargetTracks -gt 0) {
            $blockCount = [Math]::Max(1, [int][Math]::Ceiling($totalTracks / $TargetTracks))
        }
    }
    else {
        $byMin = 1
        $byTrk = 1
        if ($TargetMinutes -gt 0) { $byMin = [int][Math]::Ceiling($totalSeconds / ($TargetMinutes * 60)) }
        if ($TargetTracks -gt 0) { $byTrk = [int][Math]::Ceiling($totalTracks / $TargetTracks) }
        $blockCount = [Math]::Max(1, [Math]::Max($byMin, $byTrk))
    }

    $blocks = @()
    for ($i=0; $i -lt $blockCount; $i++) {
        $blocks += [PSCustomObject]@{
            Index = $i + 1
            Items = New-Object System.Collections.ArrayList
            Families = @{}
            TotalSeconds = 0
            TotalTracks = 0
        }
    }

    # Balanced rotation: variants of same family distributed round-robin over blocks
    $blockPointer = 0
    foreach ($family in $Families) {
        foreach ($member in $family.Members) {
            $assigned = $false
            for ($try=0; $try -lt $blocks.Count; $try++) {
                $idx = ($blockPointer + $try) % $blocks.Count
                if (-not $blocks[$idx].Families.ContainsKey($family.Family)) {
                    [void]$blocks[$idx].Items.Add($member)
                    $blocks[$idx].Families[$family.Family] = $true
                    $blocks[$idx].TotalSeconds += $member.Duration
                    $blocks[$idx].TotalTracks += 1
                    $blockPointer = ($idx + 1) % $blocks.Count
                    $assigned = $true
                    break
                }
            }

            if (-not $assigned) {
                # fallback: choose smallest block
                $targetBlock = $blocks | Sort-Object TotalTracks, TotalSeconds | Select-Object -First 1
                [void]$targetBlock.Items.Add($member)
                $targetBlock.Families[$family.Family] = $true
                $targetBlock.TotalSeconds += $member.Duration
                $targetBlock.TotalTracks += 1
            }
        }
    }

    return $blocks
}



function Get-ArtistName {
    param([string]$Name)

    $n = $Name.ToLowerInvariant()
    if ($n -match '^\s*(.+?)\s*-\s*') {
        return $matches[1].Trim()
    }

    $parts = $n -split '\s+'
    if ($parts.Count -ge 2) {
        return (($parts[0] + " " + $parts[1]).Trim())
    }
    return $n
}

function Get-EnergyBucket {
    param([string]$Name)

    $n = $Name.ToLowerInvariant()

    if ($n -match 'intro|ambient|soft|calm|downtempo|chill') { return "LOW" }
    if ($n -match 'hard|peak|pressure|freak|destroy|dark|psy|acid|rage') { return "HIGH" }
    return "MID"
}

function Optimize-BlockOrderHardcore {
    param([System.Collections.ArrayList]$Items)

    if (-not $Items -or $Items.Count -le 2) {
        return ,$Items
    }

    $remaining = New-Object System.Collections.ArrayList
    foreach ($it in $Items) { [void]$remaining.Add($it) }

    $ordered = New-Object System.Collections.ArrayList
    $lastFamily = ""
    $lastArtist = ""
    $energyCycle = @("LOW","MID","HIGH","MID")
    $energyIndex = 0

    while ($remaining.Count -gt 0) {
        $candidateIndex = -1
        $preferredEnergy = $energyCycle[$energyIndex % $energyCycle.Count]

        for ($i = 0; $i -lt $remaining.Count; $i++) {
            $cand = $remaining[$i]
            if ($cand.Family -ne $lastFamily -and $cand.Artist -ne $lastArtist -and $cand.Energy -eq $preferredEnergy) {
                $candidateIndex = $i
                break
            }
        }

        if ($candidateIndex -lt 0) {
            for ($i = 0; $i -lt $remaining.Count; $i++) {
                $cand = $remaining[$i]
                if ($cand.Family -ne $lastFamily -and $cand.Artist -ne $lastArtist) {
                    $candidateIndex = $i
                    break
                }
            }
        }

        if ($candidateIndex -lt 0) {
            for ($i = 0; $i -lt $remaining.Count; $i++) {
                $cand = $remaining[$i]
                if ($cand.Family -ne $lastFamily) {
                    $candidateIndex = $i
                    break
                }
            }
        }

        if ($candidateIndex -lt 0) { $candidateIndex = 0 }

        $chosen = $remaining[$candidateIndex]
        [void]$ordered.Add($chosen)
        $lastFamily = $chosen.Family
        $lastArtist = $chosen.Artist
        $remaining.RemoveAt($candidateIndex)
        $energyIndex++
    }

    return ,$ordered
}

function Test-PeakSafety {
    param([string]$Path)

    try {
        $output = & $FfmpegExe -i $Path -filter:a volumedetect -f null NUL 2>&1
        $maxVol = $null
        foreach ($line in $output) {
            $s = $line.ToString()
            if ($s -match 'max_volume:\s*([-\d\.]+)\s*dB') {
                $maxVol = [double]$matches[1]
            }
        }
        if ($null -ne $maxVol) {
            return [PSCustomObject]@{
                Found = $true
                MaxVolume = $maxVol
                Safe = ($maxVol -le 0.0)
            }
        }
    }
    catch { }

    return [PSCustomObject]@{
        Found = $false
        MaxVolume = 0
        Safe = $true
    }
}

function Export-AutoDjMaster {
    param(
        [string]$RootDir,
        [array]$BlockDirs
    )

    # Stage complete export before replacing the published directory.
    $streamReady = Join-Path $RootDir "STREAM_READY"
    $stageDir = Join-Path $RootDir ("_STREAM_READY_STAGE_" + [guid]::NewGuid().ToString("N"))
    Ensure-Directory $stageDir
    $masterM3U = Join-Path $stageDir "master.m3u"
    $lines = New-Object System.Collections.ArrayList
    [void]$lines.Add("#EXTM3U")

    foreach ($b in $BlockDirs) {
        $destBlock = Join-Path $stageDir (Split-Path $b -Leaf)
        Copy-Item -LiteralPath $b -Destination $destBlock -Recurse -ErrorAction Stop

        $m3u = Get-ChildItem -Path $destBlock -Filter "*.m3u" | Select-Object -First 1
        if ($m3u) {
            $content = Get-Content -Path $m3u.FullName -Encoding UTF8 | Where-Object { $_ -and $_ -notmatch '^#' }
            foreach ($line in $content) {
                [void]$lines.Add((Join-Path (Split-Path $destBlock -Leaf) $line))
            }
        }
        else {
            $audio = Get-ChildItem -Path $destBlock -File | Where-Object { $_.Extension.ToLower() -in @(".mp3",".wav") } | Sort-Object Name
            foreach ($a in $audio) {
                [void]$lines.Add((Join-Path (Split-Path $destBlock -Leaf) $a.Name))
            }
        }
    }

    Set-Content -LiteralPath $masterM3U -Value $lines -Encoding UTF8 -ErrorAction Stop
    $backupExport = $null
    if (Test-Path -LiteralPath $streamReady) {
        $backupExport = Join-Path $RootDir ("STREAM_READY_PREVIOUS_" + (Get-Date -Format "yyyyMMdd_HHmmss_fff") + "_" + [guid]::NewGuid().ToString("N"))
        Move-Item -LiteralPath $streamReady -Destination $backupExport -ErrorAction Stop
        Write-Log ("Previous STREAM_READY preserved: $backupExport")
    }
    try {
        Move-Item -LiteralPath $stageDir -Destination $streamReady -ErrorAction Stop
    }
    catch {
        if ($backupExport -and (-not (Test-Path -LiteralPath $streamReady))) {
            Move-Item -LiteralPath $backupExport -Destination $streamReady -ErrorAction Stop
        }
        throw
    }
}
function Optimize-BlockOrder {
    param([System.Collections.ArrayList]$Items)

    if (-not $Items -or $Items.Count -le 2) {
        return ,$Items
    }

    $remaining = New-Object System.Collections.ArrayList
    foreach ($it in $Items) { [void]$remaining.Add($it) }

    $ordered = New-Object System.Collections.ArrayList
    $lastFamily = ""

    while ($remaining.Count -gt 0) {
        $candidateIndex = -1
        for ($i = 0; $i -lt $remaining.Count; $i++) {
            if ($remaining[$i].Family -ne $lastFamily) {
                $candidateIndex = $i
                break
            }
        }
        if ($candidateIndex -lt 0) { $candidateIndex = 0 }

        $chosen = $remaining[$candidateIndex]
        [void]$ordered.Add($chosen)
        $lastFamily = $chosen.Family
        $remaining.RemoveAt($candidateIndex)
    }

    return ,$ordered
}

function Export-M3UPlaylist {
    param(
        [string]$BlockDir,
        [int]$BlockIndex,
        [array]$FinalFiles
    )

    $m3uPath = Join-Path $BlockDir ("BLOCK_" + ("{0:d2}" -f $BlockIndex) + ".m3u")
    $lines = New-Object System.Collections.ArrayList
    [void]$lines.Add("#EXTM3U")
    foreach ($file in $FinalFiles) {
        [void]$lines.Add($file)
    }
    Set-Content -Path $m3uPath -Value $lines -Encoding UTF8
}

function Get-RecursiveAudioFiles {
    param([string]$Folder)
    $ext = @(".mp3",".wav",".flac",".m4a",".aac",".ogg",".opus",".wma")
    return Get-ChildItem -Path $Folder -Recurse -File | Where-Object {
        $ext -contains $_.Extension.ToLower() -and
        $_.FullName -notmatch '\\_BACKUP\\' -and
        $_.FullName -notmatch '\\_WORK\\' -and
        $_.FullName -notmatch '\\_OUTPUT\\'
    }
}
function Run-PlaylistBuilder {
    param([string]$InputFolder)

    $audioFiles = Get-RecursiveAudioFiles -Folder $InputFolder
    if (-not $audioFiles -or $audioFiles.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("No supported audio files found.", "No Audio Files",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
        return
    }

    $meta = Load-MetadataProfile
    $coverPool = Get-CoverFiles
    Initialize-CoverRotation -CoverPool $coverPool

    $backupDir = Join-Path $InputFolder "_BACKUP"
    $workDir   = Join-Path $InputFolder "_WORK"
    $outputDir = Join-Path $InputFolder "_OUTPUT"
    $blockRoot = Join-Path $outputDir "BLOCKS"
    Ensure-Directory $backupDir
    Ensure-Directory $workDir
    Ensure-Directory $outputDir
    Ensure-Directory $blockRoot

    # Phase 1: complete backup first
    Run-FullBackupPhase -InputFolder $InputFolder -AudioFiles $audioFiles -BackupDir $backupDir

    $splitMode = "MINUTES"
    if ($radSplitTracks.Checked) { $splitMode = "TRACKS" }
    if ($radSplitHybrid.Checked) { $splitMode = "HYBRID" }

    $targetMinutes = 180
    $targetTracks = 40
    try { $targetMinutes = [int]$txtMinutes.Text } catch { $targetMinutes = 180 }
    try { $targetTracks = [int]$txtTracks.Text } catch { $targetTracks = 40 }

    $families = Build-VariantCatalog -AudioFiles $audioFiles
    $blocks = Build-BalancedPlaylistBlocks -Families $families -SplitMode $splitMode -TargetMinutes $targetMinutes -TargetTracks $targetTracks

    Write-Log "----------------------------------------"
    Write-Log ("PLAYLIST BUILDER START")
    Write-Log ("Files found: $($audioFiles.Count)")
    Write-Log ("Families found: $($families.Count)")
    Write-Log ("Blocks planned: $($blocks.Count)")
    Write-Log ("Variant policy: BALANCED ROTATION")
    Write-Log ("Smart Shuffle: " + (Get-CheckboxState $chkSmartShuffle))
    Write-Log ("Hardcore Mix: " + (Get-CheckboxState $chkHardcoreMix))
    Write-Log ("Export M3U: " + (Get-CheckboxState $chkExportM3U))
    Write-Log ("AutoDJ Export: " + (Get-CheckboxState $chkAutoDjExport))

    $totalToProcess = 0
    foreach ($b in $blocks) { $totalToProcess += $b.Items.Count }
    Update-OverallProgress -Current 0 -Total $totalToProcess
    $processed = 0

    $allBlockDirs = New-Object System.Collections.ArrayList
    foreach ($block in $blocks) {
        Wait-IfPausedOrAbort
        $blockDir = Join-Path $blockRoot ("BLOCK_" + ("{0:d2}" -f $block.Index))
        [void]$allBlockDirs.Add($blockDir)
        Ensure-Directory $blockDir

        $blockItems = $block.Items
        if ((Get-CheckboxState $chkSmartShuffle)) {
            if ((Get-CheckboxState $chkHardcoreMix)) {
                $blockItems = Optimize-BlockOrderHardcore -Items $block.Items
            }
            else {
                $blockItems = Optimize-BlockOrder -Items $block.Items
            }
        }

        $n = 1
        $exportedFiles = New-Object System.Collections.ArrayList
        foreach ($member in $blockItems) {
            Wait-IfPausedOrAbort
            $processed++
            Update-OverallProgress -Current $processed -Total $totalToProcess

            try {
                $file = $member.File
                Update-FileProgress -Percent 10 -Step ("Block " + $block.Index + " backup")

                $baseTitle = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                if ($chkCleanTitle.Checked) {
                    $baseTitle = Clean-Title -Name $baseTitle
                }

                $ext = Get-OutputExtension
                $workTarget = Join-Path $workDir ($baseTitle + $ext)
                if (Test-Path $workTarget) { Remove-Item -Path $workTarget -Force }

                $finalTarget = Join-Path $blockDir ((("{0:d3}" -f $n) + "_" + $baseTitle + $ext))

                $selectedCover = $null
                if ($chkCover.Checked -and $coverPool.Count -gt 0) {
                    $selectedCover = Get-NextCover
                }

                Update-FileProgress -Percent 40 -Step ("Block " + $block.Index + " FFmpeg")

                $args = Build-FfmpegArgs -InputPath $file.FullName -WorkTarget $workTarget -BaseTitle $baseTitle -Meta $meta -SelectedCover $selectedCover

                $ffmpegExit = Invoke-ControlledFFmpeg -FfmpegArguments $args
                if ($ffmpegExit -ne 0 -or -not (Test-Path $workTarget)) {
                    throw ("FFmpeg processing failed. ExitCode=" + $ffmpegExit)
                }

                Update-FileProgress -Percent 80 -Step ("Block " + $block.Index + " output")
                Copy-Item -Path $workTarget -Destination $finalTarget -Force

                Update-FileProgress -Percent 100 -Step ("Block " + $block.Index + " done")
                [void]$exportedFiles.Add((Split-Path $finalTarget -Leaf))
                if ((Get-CheckboxState $chkPeakSafety)) {
                    $peakInfo = Test-PeakSafety -Path $finalTarget
                    if ($peakInfo.Found) {
                        Write-Log ("Peak check: BLOCK $($block.Index) / $baseTitle | max_volume=$($peakInfo.MaxVolume) dB")
                        if (-not $peakInfo.Safe) {
                            Write-Log ("WARNING: Possible clipping risk detected for block $($block.Index) -> $baseTitle")
                        }
                    }
                }
                Write-Log ("BLOCK $($block.Index) -> $baseTitle | family=$($member.Family)")
                $n++
            }
            catch {
                if ($script:AbortRequested) {
                if (Test-Path -LiteralPath $workTarget) { Remove-Item -LiteralPath $workTarget -Force -ErrorAction SilentlyContinue }
                throw 'Job aborted by user.'
            }
            Write-Log ("ERROR in block $($block.Index): $($_.Exception.Message)")
                Update-FileProgress -Percent 0 -Step "Error"
            }
        }

        Wait-IfPausedOrAbort
        if ((Get-CheckboxState $chkExportM3U)) {
            Export-M3UPlaylist -BlockDir $blockDir -BlockIndex $block.Index -FinalFiles $exportedFiles
            Write-Log ("M3U exported for block $($block.Index)")
        }
    }

    Wait-IfPausedOrAbort
    if ((Get-CheckboxState $chkAutoDjExport)) {
        Export-AutoDjMaster -RootDir $outputDir -BlockDirs $allBlockDirs
        Write-Log ("STREAM_READY export created.")
    }

    Wait-IfPausedOrAbort
    Update-FileProgress -Percent 100 -Step "Playlist Build Complete"
    Write-Log ("PLAYLIST BUILDER END")
    Write-Log "----------------------------------------"
    [System.Windows.Forms.MessageBox]::Show("Playlist builder complete.", "Done",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information) | Out-Null
}

# ----------------------------------------------------------
# SECTION 5 - GUI
# ----------------------------------------------------------
$form = New-Object System.Windows.Forms.Form
$form.Text = "666SOUNDsDESIGn AutoDJ Tool V1.8.3 BUTTON FIX"
$form.Size = New-Object System.Drawing.Size(1280,980)
$form.StartPosition = "CenterScreen"
$form.AutoScaleMode = "Dpi"
$form.WindowState = "Maximized"
$form.BackColor = $ColorBackground
$form.ForeColor = $ColorGreen

$lblFolder = New-Object System.Windows.Forms.Label
$lblFolder.Text = "Audio Folder"
$lblFolder.Location = New-Object System.Drawing.Point(20,20)
$lblFolder.Size = New-Object System.Drawing.Size(150,24)
$lblFolder.Font = $FontNormal
$form.Controls.Add($lblFolder)

$txtFolder = New-Object System.Windows.Forms.TextBox
$txtFolder.Location = New-Object System.Drawing.Point(20,50)
$txtFolder.Size = New-Object System.Drawing.Size(780,28)
$txtFolder.BackColor = $ColorPanel
$txtFolder.ForeColor = $ColorGreen
$txtFolder.Font = $FontNormal
$txtFolder.Anchor = "Top,Left,Right"
$form.Controls.Add($txtFolder)

$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = "SELECT FOLDER"
$btnBrowse.Location = New-Object System.Drawing.Point(820,48)
$btnBrowse.Size = New-Object System.Drawing.Size(260,32)
$btnBrowse.BackColor = $ColorCyan
$btnBrowse.ForeColor = [System.Drawing.Color]::Black
$btnBrowse.Font = $FontNormal
$btnBrowse.Anchor = "Top,Right"
$form.Controls.Add($btnBrowse)

# Mode group
$grpMode = New-Object System.Windows.Forms.GroupBox
$grpMode.Text = "Mode"
$grpMode.Location = New-Object System.Drawing.Point(20,95)
$grpMode.Size = New-Object System.Drawing.Size(340,90)
$grpMode.ForeColor = $ColorGreen
$grpMode.Font = $FontNormal
$grpMode.Anchor = "Top,Left"
$form.Controls.Add($grpMode)

$radModeDirectory = New-Object System.Windows.Forms.RadioButton
$radModeDirectory.Text = "Directory Process"
$radModeDirectory.Location = New-Object System.Drawing.Point(15,35)
$radModeDirectory.Size = New-Object System.Drawing.Size(150,24)
$radModeDirectory.Checked = $true
$radModeDirectory.ForeColor = $ColorGreen
$grpMode.Controls.Add($radModeDirectory)

$radModePlaylist = New-Object System.Windows.Forms.RadioButton
$radModePlaylist.Text = "Playlist Builder"
$radModePlaylist.Location = New-Object System.Drawing.Point(175,35)
$radModePlaylist.Size = New-Object System.Drawing.Size(150,24)
$radModePlaylist.ForeColor = $ColorGreen
$grpMode.Controls.Add($radModePlaylist)

# Profile group
$grpProfile = New-Object System.Windows.Forms.GroupBox
$grpProfile.Text = "Profile"
$grpProfile.Location = New-Object System.Drawing.Point(380,95)
$grpProfile.Size = New-Object System.Drawing.Size(330,90)
$grpProfile.ForeColor = $ColorGreen
$grpProfile.Font = $FontNormal
$grpProfile.Anchor = "Top,Left"
$form.Controls.Add($grpProfile)

$radProfileStream = New-Object System.Windows.Forms.RadioButton
$radProfileStream.Text = "STREAM"
$radProfileStream.Location = New-Object System.Drawing.Point(15,35)
$radProfileStream.Size = New-Object System.Drawing.Size(90,24)
$radProfileStream.Checked = $true
$radProfileStream.ForeColor = $ColorGreen
$grpProfile.Controls.Add($radProfileStream)

$radProfileDj = New-Object System.Windows.Forms.RadioButton
$radProfileDj.Text = "DJ"
$radProfileDj.Location = New-Object System.Drawing.Point(110,35)
$radProfileDj.Size = New-Object System.Drawing.Size(60,24)
$radProfileDj.ForeColor = $ColorGreen
$grpProfile.Controls.Add($radProfileDj)

$radProfileCustom = New-Object System.Windows.Forms.RadioButton
$radProfileCustom.Text = "CUSTOM"
$radProfileCustom.Location = New-Object System.Drawing.Point(180,35)
$radProfileCustom.Size = New-Object System.Drawing.Size(110,24)
$radProfileCustom.ForeColor = $ColorGreen
$grpProfile.Controls.Add($radProfileCustom)

# Playlist split group
$grpSplit = New-Object System.Windows.Forms.GroupBox
$grpSplit.Text = "Playlist Split"
$grpSplit.Location = New-Object System.Drawing.Point(540,95)
$grpSplit.Size = New-Object System.Drawing.Size(640,100)
$grpSplit.ForeColor = $ColorGreen
$grpSplit.Font = $FontNormal
$grpSplit.Anchor = "Top,Left"
$form.Controls.Add($grpSplit)

$radSplitMinutes = New-Object System.Windows.Forms.RadioButton
$radSplitMinutes.Text = "By Minutes"
$radSplitMinutes.Location = New-Object System.Drawing.Point(15,35)
$radSplitMinutes.Size = New-Object System.Drawing.Size(125,24)
$radSplitMinutes.Checked = $true
$radSplitMinutes.ForeColor = $ColorGreen
$grpSplit.Controls.Add($radSplitMinutes)

$txtMinutes = New-Object System.Windows.Forms.TextBox
$txtMinutes.Location = New-Object System.Drawing.Point(115,33)
$txtMinutes.Size = New-Object System.Drawing.Size(50,24)
$txtMinutes.BackColor = $ColorPanel
$txtMinutes.ForeColor = $ColorGreen
$txtMinutes.Text = "180"
$grpSplit.Controls.Add($txtMinutes)

$radSplitTracks = New-Object System.Windows.Forms.RadioButton
$radSplitTracks.Text = "By Tracks"
$radSplitTracks.Location = New-Object System.Drawing.Point(175,35)
$radSplitTracks.Size = New-Object System.Drawing.Size(110,24)
$radSplitTracks.ForeColor = $ColorGreen
$grpSplit.Controls.Add($radSplitTracks)

$txtTracks = New-Object System.Windows.Forms.TextBox
$txtTracks.Location = New-Object System.Drawing.Point(270,33)
$txtTracks.Size = New-Object System.Drawing.Size(50,24)
$txtTracks.BackColor = $ColorPanel
$txtTracks.ForeColor = $ColorGreen
$txtTracks.Text = "40"
$grpSplit.Controls.Add($txtTracks)

$radSplitHybrid = New-Object System.Windows.Forms.RadioButton
$radSplitHybrid.Text = "Hybrid"
$radSplitHybrid.Location = New-Object System.Drawing.Point(15,66)
$radSplitHybrid.Size = New-Object System.Drawing.Size(70,24)
$radSplitHybrid.ForeColor = $ColorGreen
$grpSplit.Controls.Add($radSplitHybrid)

$chkSmartShuffle = New-Object System.Windows.Forms.CheckBox
$chkSmartShuffle.Text = "Smart Shuffle"
$chkSmartShuffle.Location = New-Object System.Drawing.Point(110,66)
$chkSmartShuffle.Size = New-Object System.Drawing.Size(120,24)
$chkSmartShuffle.Checked = $true
$chkSmartShuffle.ForeColor = $ColorGreen
$grpSplit.Controls.Add($chkSmartShuffle)

$chkExportM3U = New-Object System.Windows.Forms.CheckBox
$chkExportM3U.Text = "Export M3U"
$chkExportM3U.Location = New-Object System.Drawing.Point(255,66)
$chkExportM3U.Size = New-Object System.Drawing.Size(100,24)
$chkExportM3U.Checked = $true
$chkExportM3U.ForeColor = $ColorGreen
$grpSplit.Controls.Add($chkExportM3U)

$chkHardcoreMix = New-Object System.Windows.Forms.CheckBox
$chkHardcoreMix.Text = "Hardcore Mix"
$chkHardcoreMix.Location = New-Object System.Drawing.Point(380,66)
$chkHardcoreMix.Size = New-Object System.Drawing.Size(120,24)
$chkHardcoreMix.Checked = $true
$chkHardcoreMix.ForeColor = $ColorGreen
$grpSplit.Controls.Add($chkHardcoreMix)

$chkAutoDjExport = New-Object System.Windows.Forms.CheckBox
$chkAutoDjExport.Text = "AutoDJ Export"
$chkAutoDjExport.Location = New-Object System.Drawing.Point(380,35)
$chkAutoDjExport.Size = New-Object System.Drawing.Size(120,24)
$chkAutoDjExport.Checked = $true
$chkAutoDjExport.ForeColor = $ColorGreen
$grpSplit.Controls.Add($chkAutoDjExport)

# Format group
$grpOutput = New-Object System.Windows.Forms.GroupBox
$grpOutput.Text = "Output Audio Settings"
$grpOutput.Location = New-Object System.Drawing.Point(20,200)
$grpOutput.Size = New-Object System.Drawing.Size(1120,190)
$grpOutput.ForeColor = $ColorGreen
$grpOutput.Font = $FontNormal
$grpOutput.Anchor = "Top,Left,Right"
$form.Controls.Add($grpOutput)

$radFormatMp3 = New-Object System.Windows.Forms.RadioButton
$radFormatMp3.Text = "MP3"
$radFormatMp3.Location = New-Object System.Drawing.Point(15,30)
$radFormatMp3.Size = New-Object System.Drawing.Size(60,24)
$radFormatMp3.Checked = $true
$radFormatMp3.ForeColor = $ColorGreen
$grpOutput.Controls.Add($radFormatMp3)

$radFormatWav = New-Object System.Windows.Forms.RadioButton
$radFormatWav.Text = "WAV"
$radFormatWav.Location = New-Object System.Drawing.Point(80,30)
$radFormatWav.Size = New-Object System.Drawing.Size(60,24)
$radFormatWav.ForeColor = $ColorGreen
$grpOutput.Controls.Add($radFormatWav)

$lblBitrate = New-Object System.Windows.Forms.Label
$lblBitrate.Text = "MP3 kbps"
$lblBitrate.Location = New-Object System.Drawing.Point(160,30)
$lblBitrate.Size = New-Object System.Drawing.Size(90,24)
$lblBitrate.ForeColor = $ColorGreen
$grpOutput.Controls.Add($lblBitrate)

$cmbBitrate = New-Object System.Windows.Forms.ComboBox
$cmbBitrate.Location = New-Object System.Drawing.Point(250,28)
$cmbBitrate.Size = New-Object System.Drawing.Size(80,24)
$cmbBitrate.BackColor = $ColorPanel
$cmbBitrate.ForeColor = $ColorGreen
[void]$cmbBitrate.Items.AddRange(@("128","192","256","320"))
$cmbBitrate.SelectedItem = "128"
$grpOutput.Controls.Add($cmbBitrate)

$lblWavDepth = New-Object System.Windows.Forms.Label
$lblWavDepth.Text = "WAV Bit Depth"
$lblWavDepth.Location = New-Object System.Drawing.Point(345,30)
$lblWavDepth.Size = New-Object System.Drawing.Size(140,24)
$lblWavDepth.ForeColor = $ColorGreen
$grpOutput.Controls.Add($lblWavDepth)

$cmbWavBitDepth = New-Object System.Windows.Forms.ComboBox
$cmbWavBitDepth.Location = New-Object System.Drawing.Point(490,28)
$cmbWavBitDepth.Size = New-Object System.Drawing.Size(70,24)
$cmbWavBitDepth.BackColor = $ColorPanel
$cmbWavBitDepth.ForeColor = $ColorGreen
[void]$cmbWavBitDepth.Items.AddRange(@("16","24","32"))
$cmbWavBitDepth.SelectedItem = "16"
$grpOutput.Controls.Add($cmbWavBitDepth)

$lblSampleRate = New-Object System.Windows.Forms.Label
$lblSampleRate.Text = "Sample Rate"
$lblSampleRate.Location = New-Object System.Drawing.Point(580,30)
$lblSampleRate.Size = New-Object System.Drawing.Size(110,24)
$lblSampleRate.ForeColor = $ColorGreen
$grpOutput.Controls.Add($lblSampleRate)

$cmbSampleRate = New-Object System.Windows.Forms.ComboBox
$cmbSampleRate.Location = New-Object System.Drawing.Point(695,28)
$cmbSampleRate.Size = New-Object System.Drawing.Size(90,24)
$cmbSampleRate.BackColor = $ColorPanel
$cmbSampleRate.ForeColor = $ColorGreen
[void]$cmbSampleRate.Items.AddRange(@("44100","48000"))
$cmbSampleRate.SelectedItem = "44100"
$grpOutput.Controls.Add($cmbSampleRate)

$lblLufs = New-Object System.Windows.Forms.Label
$lblLufs.Text = "LUFS"
$lblLufs.Location = New-Object System.Drawing.Point(15,72)
$lblLufs.Size = New-Object System.Drawing.Size(50,24)
$lblLufs.ForeColor = $ColorGreen
$grpOutput.Controls.Add($lblLufs)

$txtCustomLufs = New-Object System.Windows.Forms.TextBox
$txtCustomLufs.Location = New-Object System.Drawing.Point(70,70)
$txtCustomLufs.Size = New-Object System.Drawing.Size(70,24)
$txtCustomLufs.BackColor = $ColorPanel
$txtCustomLufs.ForeColor = $ColorGreen
$txtCustomLufs.Text = "-12"
$grpOutput.Controls.Add($txtCustomLufs)

$lblTruePeak = New-Object System.Windows.Forms.Label
$lblTruePeak.Text = "True Peak"
$lblTruePeak.Location = New-Object System.Drawing.Point(160,72)
$lblTruePeak.Size = New-Object System.Drawing.Size(80,24)
$lblTruePeak.ForeColor = $ColorGreen
$grpOutput.Controls.Add($lblTruePeak)

$txtTruePeak = New-Object System.Windows.Forms.TextBox
$txtTruePeak.Location = New-Object System.Drawing.Point(245,70)
$txtTruePeak.Size = New-Object System.Drawing.Size(70,24)
$txtTruePeak.BackColor = $ColorPanel
$txtTruePeak.ForeColor = $ColorGreen
$txtTruePeak.Text = "-1"
$grpOutput.Controls.Add($txtTruePeak)

$chkNormalize = New-Object System.Windows.Forms.CheckBox
$chkNormalize.Text = "Normalize"
$chkNormalize.Location = New-Object System.Drawing.Point(340,70)
$chkNormalize.Size = New-Object System.Drawing.Size(100,24)
$chkNormalize.Checked = $true
$chkNormalize.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkNormalize)

$chkMetadata = New-Object System.Windows.Forms.CheckBox
$chkMetadata.Text = "Write Metadata"
$chkMetadata.Location = New-Object System.Drawing.Point(450,70)
$chkMetadata.Size = New-Object System.Drawing.Size(140,24)
$chkMetadata.Checked = $true
$chkMetadata.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkMetadata)

$chkCover = New-Object System.Windows.Forms.CheckBox
$chkCover.Text = "Use Cover Pool"
$chkCover.Location = New-Object System.Drawing.Point(595,70)
$chkCover.Size = New-Object System.Drawing.Size(150,24)
$chkCover.Checked = $true
$chkCover.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkCover)

$chkCleanTitle = New-Object System.Windows.Forms.CheckBox
$chkCleanTitle.Text = "Clean Title"
$chkCleanTitle.Location = New-Object System.Drawing.Point(760,70)
$chkCleanTitle.Size = New-Object System.Drawing.Size(110,24)
$chkCleanTitle.Checked = $true
$chkCleanTitle.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkCleanTitle)

$chkReplaceCover = New-Object System.Windows.Forms.CheckBox
$chkReplaceCover.Text = "Replace Embedded Cover"
$chkReplaceCover.Location = New-Object System.Drawing.Point(15,108)
$chkReplaceCover.Size = New-Object System.Drawing.Size(220,24)
$chkReplaceCover.Checked = $true
$chkReplaceCover.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkReplaceCover)

$chkPeakSafety = New-Object System.Windows.Forms.CheckBox
$chkPeakSafety.Text = "Peak Safety Check"
$chkPeakSafety.Location = New-Object System.Drawing.Point(260,108)
$chkPeakSafety.Size = New-Object System.Drawing.Size(170,24)
$chkPeakSafety.Checked = $false
$chkPeakSafety.ForeColor = $ColorGreen
$grpOutput.Controls.Add($chkPeakSafety)

if ($null -eq $chkHardcoreMix) {
    $chkHardcoreMix = New-Object System.Windows.Forms.CheckBox
    $chkHardcoreMix.Checked = $false
}
if ($null -eq $chkAutoDjExport) {
    $chkAutoDjExport = New-Object System.Windows.Forms.CheckBox
    $chkAutoDjExport.Checked = $false
}
if ($null -eq $chkPeakSafety) {
    $chkPeakSafety = New-Object System.Windows.Forms.CheckBox
    $chkPeakSafety.Checked = $false
}

$btnMetadata = New-Object System.Windows.Forms.Button
$btnMetadata.Text = "STANDARD METADATA"
$btnMetadata.Location = New-Object System.Drawing.Point(880,104)
$btnMetadata.Size = New-Object System.Drawing.Size(210,32)
$btnMetadata.BackColor = $ColorCyan
$btnMetadata.ForeColor = [System.Drawing.Color]::Black
$btnMetadata.Font = $FontNormal
$grpOutput.Controls.Add($btnMetadata)

$btnStart = New-Object System.Windows.Forms.Button
$btnStart.Text = "START"
$btnStart.Location = New-Object System.Drawing.Point(20,385)
$btnStart.Size = New-Object System.Drawing.Size(180,42)
$btnStart.BackColor = $ColorPink
$btnStart.ForeColor = [System.Drawing.Color]::Black
$btnStart.Font = $FontBold
$form.Controls.Add($btnStart)

$btnClear = New-Object System.Windows.Forms.Button
$btnClear.Text = "CLEAR LOG"
$btnClear.Location = New-Object System.Drawing.Point(220,385)
$btnClear.Size = New-Object System.Drawing.Size(140,42)
$btnClear.BackColor = $ColorCyan
$btnClear.ForeColor = [System.Drawing.Color]::Black
$btnClear.Font = $FontNormal
$form.Controls.Add($btnClear)

$btnPause = New-Object System.Windows.Forms.Button
$btnPause.Text = "PAUSE"
$btnPause.Location = New-Object System.Drawing.Point(380,385)
$btnPause.Size = New-Object System.Drawing.Size(120,42)
$btnPause.BackColor = $ColorCyan
$btnPause.ForeColor = [System.Drawing.Color]::Black
$btnPause.Font = $FontNormal
$form.Controls.Add($btnPause)

$btnAbort = New-Object System.Windows.Forms.Button
$btnAbort.Text = "ABORT"
$btnAbort.Location = New-Object System.Drawing.Point(520,385)
$btnAbort.Size = New-Object System.Drawing.Size(120,42)
$btnAbort.BackColor = $ColorPink
$btnAbort.ForeColor = [System.Drawing.Color]::Black
$btnAbort.Font = $FontNormal
$form.Controls.Add($btnAbort)

$lblCurrent = New-Object System.Windows.Forms.Label
$lblCurrent.Text = "Current Output: STREAM / MP3 / 128 kbps / 44100 / -12 LUFS / TP -1"
$lblCurrent.Location = New-Object System.Drawing.Point(660,395)
$lblCurrent.Size = New-Object System.Drawing.Size(560,24)
$lblCurrent.Font = $FontNormal
$lblCurrent.ForeColor = $ColorGreen
$lblCurrent.Anchor = "Top,Left,Right"
$form.Controls.Add($lblCurrent)

$lblOverall = New-Object System.Windows.Forms.Label
$lblOverall.Text = "Overall: 0%"
$lblOverall.Location = New-Object System.Drawing.Point(20,445)
$lblOverall.Size = New-Object System.Drawing.Size(280,24)
$lblOverall.Font = $FontNormal
$form.Controls.Add($lblOverall)

$prgOverall = New-Object System.Windows.Forms.ProgressBar
$prgOverall.Location = New-Object System.Drawing.Point(20,475)
$prgOverall.Size = New-Object System.Drawing.Size(1120,22)
$prgOverall.Anchor = "Top,Left,Right"
$form.Controls.Add($prgOverall)

$lblFile = New-Object System.Windows.Forms.Label
$lblFile.Text = "File: 0%"
$lblFile.Location = New-Object System.Drawing.Point(20,510)
$lblFile.Size = New-Object System.Drawing.Size(950,24)
$lblFile.Font = $FontNormal
$form.Controls.Add($lblFile)

$prgFile = New-Object System.Windows.Forms.ProgressBar
$prgFile.Location = New-Object System.Drawing.Point(20,540)
$prgFile.Size = New-Object System.Drawing.Size(1120,22)
$prgFile.Anchor = "Top,Left,Right"
$form.Controls.Add($prgFile)

$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Location = New-Object System.Drawing.Point(20,580)
$txtLog.Size = New-Object System.Drawing.Size(1120,320)
$txtLog.Multiline = $true
$txtLog.ScrollBars = "Both"
$txtLog.BackColor = $ColorLogBack
$txtLog.ForeColor = $ColorLogFore
$txtLog.Font = New-Object System.Drawing.Font("Consolas", 13)
$txtLog.Anchor = "Top,Bottom,Left,Right"
$form.Controls.Add($txtLog)

function Update-CurrentOutputLabel {
    $profile = Get-SelectedProfile
    $format = $(if($radFormatMp3.Checked){"MP3"}else{"WAV"})
    $bitInfo = ""
    if ($radFormatMp3.Checked) {
        $bitInfo = [string]$cmbBitrate.SelectedItem + " kbps"
    }
    else {
        $bitInfo = [string]$cmbWavBitDepth.SelectedItem + " bit"
    }
    $lblCurrent.Text = "Current Output: " + $profile + " / " + $format + " / " + $bitInfo + " / " + [string]$cmbSampleRate.SelectedItem + " / " + $txtCustomLufs.Text + " LUFS / TP " + $txtTruePeak.Text
}

# ----------------------------------------------------------
# SECTION 6 - GUI EVENTS
# ----------------------------------------------------------
$btnBrowse.Add_Click({
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = "Select audio folder"
    if ($dialog.ShowDialog() -eq "OK") {
        $txtFolder.Text = $dialog.SelectedPath
        Write-Log ("Selected folder: $($dialog.SelectedPath)")
    }
})

$btnMetadata.Add_Click({
    Show-MetadataEditor
})

$btnClear.Add_Click({
    $txtLog.Clear()
})

if ($null -eq $btnPause) {
    $btnPause = New-Object System.Windows.Forms.Button
    $btnPause.Text = "PAUSE"
    $btnPause.Location = New-Object System.Drawing.Point(380,385)
    $btnPause.Size = New-Object System.Drawing.Size(120,42)
    $btnPause.BackColor = $ColorCyan
    $btnPause.ForeColor = [System.Drawing.Color]::Black
    $btnPause.Font = $FontNormal
    $form.Controls.Add($btnPause)
}

if ($null -eq $btnAbort) {
    $btnAbort = New-Object System.Windows.Forms.Button
    $btnAbort.Text = "ABORT"
    $btnAbort.Location = New-Object System.Drawing.Point(520,385)
    $btnAbort.Size = New-Object System.Drawing.Size(120,42)
    $btnAbort.BackColor = $ColorPink
    $btnAbort.ForeColor = [System.Drawing.Color]::Black
    $btnAbort.Font = $FontNormal
    $form.Controls.Add($btnAbort)
}

$btnPause.Add_Click({
    $script:IsPaused = -not $script:IsPaused
    if ($script:IsPaused) {
        $btnPause.Text = "RESUME"
        Write-Log ("PAUSE requested")
    }
    else {
        $btnPause.Text = "PAUSE"
        Write-Log ("RESUME requested")
    }
})

$btnAbort.Add_Click({
    $script:AbortRequested = $true
    Write-Log ("ABORT requested")
})

$radProfileStream.Add_CheckedChanged({ if ($radProfileStream.Checked) { Apply-ProfileSettings; Update-CurrentOutputLabel } })
$radProfileDj.Add_CheckedChanged({ if ($radProfileDj.Checked) { Apply-ProfileSettings; Update-CurrentOutputLabel } })
$radProfileCustom.Add_CheckedChanged({ if ($radProfileCustom.Checked) { Update-CurrentOutputLabel } })

$radFormatMp3.Add_CheckedChanged({ Update-FormatUiState; Update-CurrentOutputLabel })
$radFormatWav.Add_CheckedChanged({ Update-FormatUiState; Update-CurrentOutputLabel })
$cmbBitrate.Add_SelectedIndexChanged({ Update-CurrentOutputLabel })
$cmbWavBitDepth.Add_SelectedIndexChanged({ Update-CurrentOutputLabel })
$cmbSampleRate.Add_SelectedIndexChanged({ Update-CurrentOutputLabel })
$txtCustomLufs.Add_TextChanged({ Update-CurrentOutputLabel })
$txtTruePeak.Add_TextChanged({ Update-CurrentOutputLabel })

$btnStart.Add_Click({
    try {
        $script:AbortRequested = $false
        $script:IsPaused = $false
        $btnPause.Text = "PAUSE"
        $inputFolder = $txtFolder.Text.Trim()
        if ([string]::IsNullOrWhiteSpace($inputFolder) -or -not (Test-Path $inputFolder)) {
            [System.Windows.Forms.MessageBox]::Show(
                "Please select a valid audio folder first.",
                "Missing Folder",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Warning
            ) | Out-Null
            return
        }

        if (-not (Ensure-FFmpeg)) { return }

        if ($radModeDirectory.Checked) {
            Run-DirectoryProcess -InputFolder $inputFolder
        }
        else {
            Run-PlaylistBuilder -InputFolder $inputFolder
        }
    }
    catch {
        Write-CriticalError ($_.Exception.Message)
        [System.Windows.Forms.MessageBox]::Show(
            "Critical error:" + "`r`n" + $_.Exception.Message,
            "Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        ) | Out-Null
    }
})

# ----------------------------------------------------------
# SECTION 7 - INITIAL STATE
# ----------------------------------------------------------
Apply-ProfileSettings
Update-CurrentOutputLabel
Write-Log ("Tool ready.")
Write-Log ("Final fix mode active.")
Write-Log ("Peak safety default: " + (Get-CheckboxState $chkPeakSafety))
Write-Log ("Bundled covers: $((Get-CoverFiles).Count)")
$form.ShowDialog() | Out-Null
