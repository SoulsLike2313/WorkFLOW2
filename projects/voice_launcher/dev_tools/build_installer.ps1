param(
    [string]$PythonExe = "python",
    [switch]$SkipPortable
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not $SkipPortable) {
    & "$PSScriptRoot\build_portable.ps1" -PythonExe $PythonExe
}

$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) {
    $iscc = "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
}
if (-not (Test-Path $iscc)) {
    throw "Inno Setup (ISCC.exe) not found. Please install Inno Setup 6."
}

Write-Host "== Build installer =="
Push-Location "installer"
& $iscc "VoiceLauncherInstaller.iss" | Out-Host
Pop-Location

Write-Host "Installer ready: installer\output\VoiceLauncherSetup.exe"
