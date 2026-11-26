# Release-only Windows artifact gate; no mutation of output files.
[CmdletBinding()]param(
 [ValidateSet('Setup','Portable','Both')][string]$Target='Both',
 [Parameter(Mandatory=$true)][string]$BuildStartedAt
)
$ErrorActionPreference='Stop'
$startUtc=[datetime]::Parse($BuildStartedAt,[Globalization.CultureInfo]::InvariantCulture,[Globalization.DateTimeStyles]::RoundtripKind).ToUniversalTime()
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$pkg=Get-Content (Join-Path $root 'package.json') -Raw | ConvertFrom-Json
$dir=Join-Path $root 'dist'
if(-not(Test-Path $dir)){throw 'Electron dist fehlt nach Build'}
$names=@()
if($Target -in @('Setup','Both')){$names+= "666_CHATBACKUP_ELECTRON_SETUP_$($pkg.version).exe"}
if($Target -in @('Portable','Both')){$names+= "666_CHATBACKUP_ELECTRON_PORTABLE_$($pkg.version)_x64.exe"}
$items=@()
foreach($name in $names){
 $f=Join-Path $dir $name
 if(-not(Test-Path -LiteralPath $f -PathType Leaf)){throw "Build-Ausgabe fehlt: $name"}
 $info=Get-Item -LiteralPath $f
 if($info.Length -lt 1000000){throw "Build-Ausgabe ungewoehnlich klein: $name"}
 if($info.LastWriteTimeUtc -lt $startUtc.AddSeconds(-3)){throw "Altes Build-Artefakt statt frischer Ausgabe: $name"}
 $sha=(Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
 $items+=@{name=$name;size=$info.Length;sha256=$sha;modified_utc=$info.LastWriteTimeUtc.ToString('o')}
 Write-Host "BUILD VERIFIED $name SHA256=$sha" -ForegroundColor Green
}
$report=@{project='666 CHATBACKUP PC TOOL';version=$pkg.version;target=$Target;artifacts=$items;host=$env:COMPUTERNAME;created_utc=[datetime]::UtcNow.ToString('o')}
$reportPath=Join-Path $dir 'BUILD_ARTIFACT_READBACK.json'
[IO.File]::WriteAllText($reportPath,($report|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
Write-Host "Build-Readback erstellt: $reportPath" -ForegroundColor Cyan
