$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Missing virtual environment. Run run_setup.ps1 first."
}

& .\.venv\Scripts\python.exe -m app.verify
if ($LASTEXITCODE -ne 0) {
    throw "Machine Verification Gate did not pass. User mode launch aborted."
}

& .\.venv\Scripts\python.exe -m app.launcher user --skip-gate-check
