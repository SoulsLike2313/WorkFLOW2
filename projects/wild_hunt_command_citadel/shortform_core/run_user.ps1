param(
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Missing virtual environment. Run run_setup.ps1 first."
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$startupScript = Resolve-Path (Join-Path $projectRoot "..\..\..\scripts\project_startup.py")
$startupRaw = & $pythonExe $startupScript prepare --project-slug shortform_core --startup-kind user --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for shortform_core user mode."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

& $pythonExe -m app.verify
if ($LASTEXITCODE -ne 0) {
    throw "Machine Verification Gate did not pass. User mode launch aborted."
}

& $pythonExe -m app.launcher user --skip-gate-check
