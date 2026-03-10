$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt

& $pythonExe -m app.main
& $pythonExe -m app.bootstrap_v2

$uvicornCommand = ".\.venv\Scripts\python.exe -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload"
Write-Host ""
Write-Host "Команда запуска Uvicorn:"
Write-Host $uvicornCommand
