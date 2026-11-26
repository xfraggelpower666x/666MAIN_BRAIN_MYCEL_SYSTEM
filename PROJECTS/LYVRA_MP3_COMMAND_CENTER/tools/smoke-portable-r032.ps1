# R03.2: Paketstart mit eingeschränktem PATH und unabhängigem Receipt.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$dist=Join-Path $root 'dist/win-unpacked'
$exe=Join-Path $dist 'lyvra-mp3-command-center.exe'
if(!(Test-Path $exe)){throw 'EXE fehlt'}
$resources=Join-Path $dist 'resources'
foreach($rel in @('app.asar','workers/tools/probe_mp3.py','workers/tools/restore_worker.py','workers/originals/mp3/ELECTRON_CANDIDATE/engine_bridge.py','runtime/python/python.exe','runtime/ffmpeg/ffmpeg.exe','runtime/ffmpeg/ffprobe.exe')){
 if(!(Test-Path (Join-Path $resources $rel))){throw "Paketressource fehlt: $rel"}
}
$oldPath=$env:PATH
try{
 $env:PATH="$env:SystemRoot/System32;$env:SystemRoot"
 foreach($name in @('LYVRA_PYTHON','LYVRA_FFMPEG','LYVRA_FFPROBE','PYTHONHOME','PYTHONPATH','VIRTUAL_ENV')){Remove-Item "Env:$name" -ErrorAction SilentlyContinue}
 $proc=Start-Process -FilePath $exe -ArgumentList '--lyvra-smoke' -WorkingDirectory $dist -PassThru
 if(!$proc.WaitForExit(120000)){Stop-Process -Id $proc.Id -Force;throw 'GUI timeout'}
 if($proc.ExitCode -ne 0){throw "GUI exit $($proc.ExitCode)"}
 $receipt=Join-Path ([IO.Path]::GetTempPath()) "lyvra-r032-$($proc.Id).json"
 if(!(Test-Path $receipt)){throw 'GUI receipt fehlt'}
 $data=Get-Content -LiteralPath $receipt -Raw | ConvertFrom-Json
 if($data.status -ne 'PASS' -or !$data.packaged -or !$data.visible){throw 'GUI receipt ungültig'}
 foreach($key in @('workerRoot','python','ffmpeg','ffprobe')){
  if(!([IO.Path]::GetFullPath($data.$key).StartsWith([IO.Path]::GetFullPath($resources)+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase))){throw "Externe Runtime: $key"}
 }
 Get-Content -LiteralPath $receipt -Raw
 Get-FileHash -LiteralPath $exe -Algorithm SHA256
 Write-Output "WINDOWS_BUILD_PASS commit=$env:GITHUB_SHA"
 Write-Output "PACKAGED_GUI_SMOKE_PASS commit=$env:GITHUB_SHA"
}finally{$env:PATH=$oldPath}
