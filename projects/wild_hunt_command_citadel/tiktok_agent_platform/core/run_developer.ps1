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
$startupRaw = & $pythonExe $startupScript prepare --project-slug tiktok_agent_platform --startup-kind developer --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for tiktok_agent_platform developer mode."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

$apiPort = [int]$startup.selected_ports.api_port
$apiHost = "127.0.0.1"
$apiBase = "http://$apiHost`:$apiPort"

Write-Host "Developer mode (runtime namespace: tiktok_agent_platform):"
Write-Host "1) Backend API: .\.venv\Scripts\python.exe -m app.launcher developer backend --host $apiHost --port $apiPort"
Write-Host "2) Desktop UI: .\.venv\Scripts\python.exe -m app.launcher developer ui --api-base-url $apiBase"
Write-Host "3) Verify:      .\.venv\Scripts\python.exe -m app.verify"
Write-Host "4) User update: powershell -ExecutionPolicy Bypass -File .\run_update.ps1 -Mode check -PortMode $PortMode -ManifestPath <manifest.json>"
Write-Host ""
Write-Host "Startup diagnostics:"
Write-Host "- $($startup.startup_report_json)"
