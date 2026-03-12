param(
    [ValidateSet("check", "apply", "post-verify")]
    [string]$Mode = "check",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed",
    [string]$ManifestPath = "",
    [string]$BundlePath = "",
    [string]$TargetVersion = ""
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
$startupRaw = & $pythonExe $startupScript prepare --project-slug tiktok_agent_platform --startup-kind update --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for tiktok_agent_platform update mode."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

$outputDir = [string]$startup.runtime_paths.data_dir
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

if ($Mode -eq "check") {
    if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
        throw "For check mode provide -ManifestPath <path-to-manifest.json>."
    }
    $jsonOut = Join-Path $outputDir "update_check_result.json"
    & $pythonExe -m app.update_cli check --manifest $ManifestPath --json-out $jsonOut
    exit $LASTEXITCODE
}

if ($Mode -eq "apply") {
    if ([string]::IsNullOrWhiteSpace($BundlePath)) {
        throw "For apply mode provide -BundlePath <path-to-patch-bundle>."
    }
    if ([string]::IsNullOrWhiteSpace($TargetVersion)) {
        throw "For apply mode provide -TargetVersion <version-label>."
    }
    $jsonOut = Join-Path $outputDir "update_apply_result.json"
    & $pythonExe -m app.update_cli apply --bundle $BundlePath --target-version $TargetVersion --json-out $jsonOut
    exit $LASTEXITCODE
}

$verifyOut = Join-Path $outputDir "update_post_verify_result.json"
& $pythonExe -m app.update_cli post-verify --json-out $verifyOut
exit $LASTEXITCODE
