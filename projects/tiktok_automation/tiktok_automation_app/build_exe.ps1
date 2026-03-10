param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[build] .venv not found. Running setup..."
    & powershell -ExecutionPolicy Bypass -File ".\run_setup.ps1"
}

Write-Host "[build] Installing PyInstaller"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install pyinstaller

if ($Clean) {
    if (Test-Path ".\build") { Remove-Item ".\build" -Recurse -Force }
    if (Test-Path ".\dist") { Remove-Item ".\dist" -Recurse -Force }
}

Write-Host "[build] Building EXE..."
& $venvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "WitcherCommandDeck" `
    --collect-submodules playwright `
    app.py

Write-Host ""
Write-Host "EXE created:"
Write-Host "  .\dist\WitcherCommandDeck.exe"
