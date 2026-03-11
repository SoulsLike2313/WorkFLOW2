param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "== Voice Launcher portable build =="
& $PythonExe -m pip install --upgrade pyinstaller | Out-Host
& $PythonExe -m PyInstaller --noconfirm --clean VoiceLauncher.spec | Out-Host

$portableDir = Join-Path (Get-Location) "dist\portable"
if (Test-Path $portableDir) {
    Remove-Item $portableDir -Recurse -Force
}
New-Item -ItemType Directory -Path $portableDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $portableDir "config") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $portableDir "assets") | Out-Null

Copy-Item "dist\VoiceLauncher.exe" -Destination $portableDir -Force
Copy-Item "config\*.json" -Destination (Join-Path $portableDir "config") -Force -ErrorAction SilentlyContinue
Copy-Item "assets\*.ico" -Destination (Join-Path $portableDir "assets") -Force -ErrorAction SilentlyContinue

Write-Host "Portable build ready: $portableDir"
