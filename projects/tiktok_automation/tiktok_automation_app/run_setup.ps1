$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "[setup] Creating virtual environment (.venv)"
    & python -m venv .venv
}

Write-Host "[setup] Upgrading pip"
& $venvPython -m pip install --upgrade pip

Write-Host "[setup] Installing requirements"
& $venvPython -m pip install -r requirements.txt

Write-Host "[setup] Installing Playwright Chromium"
& $venvPython -m playwright install chromium

Write-Host ""
Write-Host "Setup completed."
Write-Host "Run UI (no console):"
Write-Host "  .\.venv\Scripts\pythonw.exe .\app.py"
Write-Host ""
Write-Host "Run UI (console):"
Write-Host "  .\.venv\Scripts\python.exe .\app.py"
