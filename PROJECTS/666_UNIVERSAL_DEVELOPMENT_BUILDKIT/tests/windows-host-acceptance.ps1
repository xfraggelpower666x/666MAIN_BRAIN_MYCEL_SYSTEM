# 666 UNIVERSAL BUILDKIT R01.11.3 — Windows Host Acceptance
# No install, no upgrade, no background jobs; all builds require explicit approval.
param(
  [ValidateSet('source','gui','portable','setup','all')][string]$Mode='source',
  [Parameter(Mandatory=$true)][string]$SourceDir
)
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath($SourceDir)
if(-not(Test-Path (Join-Path $Root 'SHA256_MANIFEST.json'))){throw 'SHA256_MANIFEST.json missing'}
$Directory=Join-Path $env:LOCALAPPDATA '666SOUNDsDESIGn\UniversalBuildkit\acceptance'
New-Item -ItemType Directory -Force -Path $Directory | Out-Null
$Log=Join-Path $Directory ('R01_11_3_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.txt')
function Log([string]$Message){('['+(Get-Date -Format 's')+'] '+$Message)|Tee-Object -FilePath $Log -Append | Out-Host}
Log 'WINDOWS HOST ACCEPTANCE START. No automatic installs.'
Log ('Source='+$Root)
Log ('OS='+[Environment]::OSVersion.VersionString)
Log ('PowerShell='+$PSVersionTable.PSVersion.ToString())
$manifest=Get-Content -LiteralPath (Join-Path $Root 'SHA256_MANIFEST.json') -Raw -Encoding UTF8|ConvertFrom-Json
$count=0
foreach($entry in $manifest.files){
  $file=[IO.Path]::GetFullPath((Join-Path $Root ($entry.path -replace '/','\')))
  if(-not $file.StartsWith(($Root.TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)){throw "Path escape: $($entry.path)"}
  if(-not(Test-Path -LiteralPath $file -PathType Leaf)){throw "Missing file: $($entry.path)"}
  $hash=(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
  if($hash -ne $entry.sha256.ToLowerInvariant()){throw "Hash mismatch: $($entry.path)"}
  $count++
}
Log ("Source validation PASS: $count files")
if($Mode -eq 'source'){Log 'Windows runtime not attempted. MODE SOURCE.';exit 0}
if($Mode -in @('gui','all')){
  Log 'Launching build manager for manual visual acceptance. No hidden GUI success inferred.'
  Start-Process -FilePath (Join-Path $Root 'BUILD_MANAGER.bat') -WorkingDirectory $Root -Wait
  $answer=Read-Host 'Did the 8-second HUD lead to the build manager without a black background console? Enter PASS or FAIL'
  if($answer -cne 'PASS'){Log 'GUI HOST ACCEPTANCE FAILED OR NOT CONFIRMED';exit 2}
  Log 'GUI HOST ACCEPTANCE USER-CONFIRMED PASS'
}
$targets=if($Mode -eq 'all'){@('portable','setup')}elseif($Mode -in @('portable','setup')){@($Mode)}else{@()}
foreach($target in $targets){
  Log "Build selected: $target. Build manager may ask for tool and package install approval."
  $answer=Read-Host "Run $target via configured existing engine? Type JA"
  if($answer -cne 'JA'){Log "Build $target cancelled";exit 3}
  $ps=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
  & $ps -NoLogo -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root 'STARTEN.ps1') -Action $target 2>&1|Tee-Object -FilePath $Log -Append|Out-Host
  if($LASTEXITCODE -ne 0){Log "BUILD FAILED exit=$LASTEXITCODE";exit 4}
  $dist=Join-Path $Root 'dist'
  $executables=@(Get-ChildItem -LiteralPath $dist -Filter '*.exe' -File -ErrorAction SilentlyContinue)
  if(-not $executables.Count){Log "NO EXE found in $dist";exit 5}
  Log ("Executable artifacts present: "+($executables.Name -join ', '))
  $answer=Read-Host 'Have you started the resulting Windows artifact and verified its UI and settings persistence? PASS/FAIL'
  if($answer -cne 'PASS'){Log 'Artifact HOST ACCEPTANCE FAILED OR NOT CONFIRMED';exit 6}
  Log "Artifact $target user-confirmed PASS"
}
Log 'Selected Windows acceptance modes user-confirmed PASS. Review detailed log; manual GUI confirmation is not automated evidence.'
