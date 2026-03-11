$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Missing virtual environment. Run run_setup.ps1 first."
}

Write-Host "Developer mode:"
Write-Host "1) Backend API: .\.venv\Scripts\python.exe -m app.launcher developer backend --host 127.0.0.1 --port 8000"
Write-Host "2) Desktop UI: .\.venv\Scripts\python.exe -m app.launcher developer ui --api-base-url http://127.0.0.1:8000"
Write-Host "3) Verify:      .\.venv\Scripts\python.exe -m app.launcher developer verify"

