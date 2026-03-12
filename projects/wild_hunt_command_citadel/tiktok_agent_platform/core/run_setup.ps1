param(
    [ValidateSet("user", "developer")]
    [string]$Mode = "user",
    [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt

if (-not $SkipVerify) {
    & $pythonExe -m app.verify
    if ($LASTEXITCODE -ne 0) {
        throw "Machine Verification Gate did not pass. Fix issues before user-mode manual testing."
    }
}

if ($Mode -eq "user") {
    & $pythonExe -m app.launcher user --skip-gate-check
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Developer mode commands:"
Write-Host "  Backend: .\.venv\Scripts\python.exe -m app.launcher developer backend --host 127.0.0.1 --port 8000"
Write-Host "  UI only: .\.venv\Scripts\python.exe -m app.launcher developer ui --api-base-url http://127.0.0.1:8000"
Write-Host "  Verify:  .\.venv\Scripts\python.exe -m app.launcher developer verify"
