$ErrorActionPreference = "Stop"

param(
    [ValidateSet("intake", "audit", "verify")]
    [string]$Mode = "intake",
    [string]$TargetProjectPath = "",
    [string]$TargetProjectSlug = "",
    [switch]$ExecuteVerification
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$cursor = $projectRoot
$repoRoot = $null
while ($true) {
    if (Test-Path (Join-Path $cursor "workspace_config\\workspace_manifest.json")) {
        $repoRoot = $cursor
        break
    }
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor) {
        throw "Unable to locate workspace root from project path: $projectRoot"
    }
    $cursor = $parent
}

Set-Location $repoRoot

if ($Mode -eq "intake") {
    python .\projects\platform_test_agent\scripts\test_agent_core.py --mode intake --target-project-path $TargetProjectPath --target-project-slug $TargetProjectSlug
    exit $LASTEXITCODE
}

if ($Mode -eq "verify") {
    if ([string]::IsNullOrWhiteSpace($TargetProjectSlug)) {
        throw "TargetProjectSlug is required for verify mode."
    }
    $execFlag = ""
    if ($ExecuteVerification) { $execFlag = "--execute-verification" }
    python .\projects\platform_test_agent\scripts\test_agent_core.py --mode verify --target-project-slug $TargetProjectSlug $execFlag
    exit $LASTEXITCODE
}

if ([string]::IsNullOrWhiteSpace($TargetProjectSlug)) {
    throw "TargetProjectSlug is required for audit mode."
}

if ([string]::IsNullOrWhiteSpace($TargetProjectPath)) {
    throw "TargetProjectPath is required for audit mode."
}

$execFlag = ""
if ($ExecuteVerification) { $execFlag = "--execute-verification" }
python .\projects\platform_test_agent\scripts\test_agent_core.py --mode audit --target-project-path $TargetProjectPath --target-project-slug $TargetProjectSlug $execFlag
exit $LASTEXITCODE
