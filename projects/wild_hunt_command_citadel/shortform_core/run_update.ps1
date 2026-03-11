$ErrorActionPreference = "Stop"

param(
    [ValidateSet("check", "apply", "post-verify")]
    [string]$Mode = "check",
    [string]$ManifestPath = "",
    [string]$BundlePath = "",
    [string]$TargetVersion = ""
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    throw "Missing virtual environment. Run run_setup.ps1 first."
}

$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$outputDir = Join-Path $projectRoot "runtime\output"
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
