$ErrorActionPreference = "Stop"

param(
    [ValidateSet("intake", "audit", "verify")]
    [string]$Mode = "intake",
    [string]$TargetProjectPath = "",
    [string]$TargetProjectSlug = ""
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
    python .\scripts\validate_workspace.py
    python .\scripts\check_repo_sync.py --remote origin --branch main
    Write-Output "platform_test_agent intake complete"
    exit $LASTEXITCODE
}

if ($Mode -eq "verify") {
    if ([string]::IsNullOrWhiteSpace($TargetProjectSlug)) {
        throw "TargetProjectSlug is required for verify mode."
    }
    python .\scripts\project_startup.py run --project-slug $TargetProjectSlug --entrypoint verify --startup-kind verify --port-mode fixed
    exit $LASTEXITCODE
}

if ([string]::IsNullOrWhiteSpace($TargetProjectSlug)) {
    throw "TargetProjectSlug is required for audit mode."
}

if ([string]::IsNullOrWhiteSpace($TargetProjectPath)) {
    throw "TargetProjectPath is required for audit mode."
}

python .\scripts\validate_workspace.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python .\scripts\project_startup.py run --project-slug $TargetProjectSlug --entrypoint verify --startup-kind verify --port-mode fixed
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "platform_test_agent audit baseline complete for $TargetProjectSlug ($TargetProjectPath)"
exit 0
