# Controlled source publication only — isolated Buildkit candidate branch.
$ErrorActionPreference='Stop'
$Root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$OwnerRepo='xfraggelpower666x/666MAIN_BRAIN_MYCEL_SYSTEM'
$Branch='buildkit/r01-11-electron-source-candidate-20261125'
$Prefix='PROJECTS/666_UNIVERSAL_DEVELOPMENT_BUILDKIT'
$RepoUrl='https://github.com/'+$OwnerRepo+'.git'
$ManifestPath=Join-Path $Root 'SHA256_MANIFEST.json'
if(-not (Get-Command git -ErrorAction SilentlyContinue)){throw 'Git ist nicht installiert. Keine Aenderung ausgefuehrt.'}
if(-not (Test-Path $ManifestPath)){throw 'Source manifest fehlt.'}
$manifest=Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if(-not $manifest.files -or @($manifest.files).Count -lt 46){throw 'Source manifest unvollstaendig. STOP.'}
foreach($f in $manifest.files){
  $src=Join-Path $Root ($f.path -replace '/','\')
  $full=[IO.Path]::GetFullPath($src)
  if(-not $full.StartsWith(($Root.TrimEnd('\')+'\'),[StringComparison]::OrdinalIgnoreCase)){throw 'Pfad ausserhalb des Buildkits im Manifest.'}
  if(-not(Test-Path -LiteralPath $full -PathType Leaf)){throw "Quelldatei fehlt: $($f.path)"}
  $hash=(Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash.ToLowerInvariant()
  if($hash -cne $f.sha256.ToLowerInvariant()){throw "SHA256 passt nicht: $($f.path)"}
}
Write-Host 'Quelldateien und SHA256 verifiziert.' -ForegroundColor Cyan
Write-Host "Ziel: $OwnerRepo -> Branch $Branch -> $Prefix" -ForegroundColor Cyan
$approved=(Read-Host 'Originale Quelldateien auf diesen isolierten GitHub-Branch pushen? JA').Trim()
if($approved -cne 'JA'){Write-Host 'Abbruch: keine Writes.';exit 0}
$tmp=Join-Path ([IO.Path]::GetTempPath()) ('666-buildkit-publish-'+[Guid]::NewGuid().ToString('N'))
try {
  & git clone --quiet --single-branch --branch $Branch $RepoUrl $tmp
  if($LASTEXITCODE -ne 0){throw 'Git clone/auth fehlgeschlagen; keine Writes.'}
  Push-Location $tmp
  try {
    & git config core.autocrlf false
    if($LASTEXITCODE -ne 0){throw 'Git lokaler Autocrlf-Guard fehlgeschlagen'}
    $before=(& git rev-parse HEAD).Trim()
    if($LASTEXITCODE -ne 0){throw 'Start-Commit nicht lesbar'}
    $backup='refs/heads/backup/buildkit-r01-11-pre-publish-'+[DateTime]::UtcNow.ToString('yyyyMMddHHmmss')
    & git push origin ("HEAD:"+$backup)
    if($LASTEXITCODE -ne 0){throw 'Pre-change Branch-Backup fehlgeschlagen. STOP.'}
    $target=Join-Path $tmp ($Prefix -replace '/','\')
    foreach($f in $manifest.files){
      $dest=Join-Path $target ($f.path -replace '/','\')
      $source=Join-Path $Root ($f.path -replace '/','\')
      [void][IO.Directory]::CreateDirectory((Split-Path -Parent $dest))
      Copy-Item -LiteralPath $source -Destination $dest -Force
      if((Get-FileHash $dest -Algorithm SHA256).Hash.ToLowerInvariant() -cne $f.sha256.ToLowerInvariant()){throw "Ziel-SHA256 falsch: $($f.path)"}
    }
    Copy-Item -LiteralPath $ManifestPath -Destination (Join-Path $target 'SHA256_MANIFEST.json') -Force
    & git add -- $Prefix
    if($LASTEXITCODE -ne 0){throw 'Git stage fehlgeschlagen'}
    $changes=@(& git diff --cached --name-only)
    if($LASTEXITCODE -ne 0){throw 'Git scope check fehlgeschlagen'}
    foreach($change in $changes){if(-not $change.StartsWith($Prefix+'/')){throw "Aenderung ausserhalb des Zielpfades: $change"}}
    if($changes.Count -eq 0){Write-Host 'Keine neuen Unterschiede zum Repository.'}
    else {
      & git commit -m 'buildkit: publish complete R01.11.1 source and artwork without foreign changes'
      if($LASTEXITCODE -ne 0){throw 'Git commit fehlgeschlagen; Nutzer-Git-Identitaet pruefen'}
      & git push origin ("HEAD:refs/heads/"+$Branch)
      if($LASTEXITCODE -ne 0){throw 'Git push abgelehnt, kein Force. Branch-Konflikt manuell pruefen.'}
    }
    $newHead=(& git rev-parse HEAD).Trim()
    $remote=((& git ls-remote origin ('refs/heads/'+$Branch)) -split '\s+')[0]
    if($newHead -cne $remote){throw 'READBACK_PENDING: Remote-HEAD stimmt nicht.'}
    foreach($f in $manifest.files){
      $path=$Prefix+'/'+$f.path
      $remoteBlob=(& git rev-parse ('HEAD:'+ $path)).Trim()
      $localBlob=(& git hash-object (Join-Path $Root ($f.path -replace '/','\'))).Trim()
      if($remoteBlob -cne $localBlob){throw "GIT_BLOB_READBACK_MISMATCH: $path"}
    }
    Write-Host "VERIFIZIERT: $newHead — $(@($manifest.files).Count) Source-Blobs gelesen, Manifest SHA-256 PASS." -ForegroundColor Green
    Write-Host "Pre-change backup at $backup ($before)" -ForegroundColor DarkGray
    Write-Host 'Nicht automatisch auf 666MAIN_BRAIN gemergt. Produktionspromotion ist getrennt.'
  }finally{Pop-Location}
}finally{if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue}}
