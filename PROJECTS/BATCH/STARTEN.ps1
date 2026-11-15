# (c) 2026 666SOUNDsDESIGn - FRAGGLEPOWER666
$starter = Join-Path $PSScriptRoot 'toolstarter.py'
$forward = $args
foreach ($name in @('py.exe', 'python.exe')) {
    $interpreter = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $interpreter) { continue }
    $prefix = @()
    if ($name -eq 'py.exe') { $prefix = @('-3') }
    & $interpreter.Source @prefix -c 'import sys;sys.exit(sys.version_info < (3, 10))' 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $interpreter.Source @prefix $starter @forward
        exit $LASTEXITCODE
    }
}
Write-Error 'Python 3.10 or later was not found. Install CPython with Tcl/Tk for the graphical window.'
exit 1
