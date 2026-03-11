$ErrorActionPreference = "Stop"

param(
    [ValidateSet("user", "developer", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$repoRoot = Resolve-Path (Join-Path $projectRoot "..\..\..")
$startupScript = Join-Path $repoRoot "scripts\project_startup.py"

$startupRaw = & python $startupScript prepare --project-slug tiktok_automation_app --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for tiktok_automation_app."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

if ($Mode -eq "verify") {
    & python -m py_compile app.py automation_engine.py ui_main.py
    exit $LASTEXITCODE
}

if ($Mode -eq "developer") {
    & powershell -ExecutionPolicy Bypass -File .\run_setup.ps1
    exit $LASTEXITCODE
}

& python .\app.py
exit $LASTEXITCODE
