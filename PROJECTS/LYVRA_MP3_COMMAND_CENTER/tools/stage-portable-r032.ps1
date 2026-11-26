# R03.2: isolierte CI-Runtime, keine Veröffentlichung von Binärdateien.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$runtime=Join-Path $root 'runtime'
$py=Join-Path $runtime 'python'
$ff=Join-Path $runtime 'ffmpeg'
if((Test-Path $py) -or (Test-Path $ff)){throw 'Runtime-Ziel bereits vorhanden; kein Überschreiben'}
$base=(& python -c "import sys; print(sys.base_prefix)").Trim()
if($LASTEXITCODE -ne 0 -or !(Test-Path (Join-Path $base 'python.exe'))){throw 'Setup-Python fehlt'}
New-Item -ItemType Directory -Path $py,$ff | Out-Null
# Vollständige CPython-Laufzeit aus dem offiziellen Actions-Toolcache, kein venv-Redirect.
Copy-Item -Path (Join-Path $base '*') -Destination $py -Recurse
$python=Join-Path $py 'python.exe'
& $python -m pip install --disable-pip-version-check --no-cache-dir -r (Join-Path $root 'requirements.txt')
if($LASTEXITCODE -ne 0){throw 'Python-Abhängigkeiten fehlgeschlagen'}
# Windows-Runner-Toolcache oder Chocolatey-Repository; keine Originalassets verwenden.
$ffmpeg=Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
$ffprobe=Get-Command ffprobe.exe -ErrorAction SilentlyContinue
if(!$ffmpeg -or !$ffprobe){
  choco install ffmpeg --version=7.1.1 --yes --no-progress
  if($LASTEXITCODE -ne 0){throw 'FFmpeg Provider-Installation fehlgeschlagen'}
}
$tools=@(Get-ChildItem "$env:ChocolateyInstall/lib/ffmpeg/tools" -Recurse -Filter ffmpeg.exe -ErrorAction SilentlyContinue)
if($tools.Count -gt 0){$bin=$tools[0].Directory.FullName}
else{
  $cmd=Get-Command ffmpeg.exe -ErrorAction Stop
  $bin=Split-Path $cmd.Source
}
foreach($name in @('ffmpeg.exe','ffprobe.exe')){
  $src=Join-Path $bin $name
  if(!(Test-Path $src)){throw "Provider-Datei fehlt: $name"}
  Copy-Item -LiteralPath $src -Destination $ff
  & (Join-Path $ff $name) -version
  if($LASTEXITCODE -ne 0){throw "$name nicht ausführbar"}
  Get-FileHash -LiteralPath (Join-Path $ff $name) -Algorithm SHA256
}
& $python -I -c "import sys,mutagen,numpy,scipy,soundfile,pywt,pyloudnorm; print(sys.executable); print(sys.prefix)"
if($LASTEXITCODE -ne 0){throw 'Runtime-Importprüfung fehlgeschlagen'}
Get-FileHash -LiteralPath $python -Algorithm SHA256
Write-Output "RUNTIME_STAGE_PASS commit=$env:GITHUB_SHA provider=actions-python-toolcache/chocolatey-or-runner"
