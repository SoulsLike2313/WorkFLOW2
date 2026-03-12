param(
    [ValidateSet("user", "developer", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$cursor = $projectRoot
$repoRoot = $null
while ($true) {
    if (Test-Path (Join-Path $cursor "workspace_config\workspace_manifest.json")) {
        $repoRoot = $cursor
        break
    }
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor) {
        throw "Unable to locate workspace root from project path: $projectRoot"
    }
    $cursor = $parent
}

$startupScript = Join-Path $repoRoot "scripts\project_startup.py"

$startupRaw = & python $startupScript prepare --project-slug tiktok_agent_platform --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for tiktok_agent_platform."
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
