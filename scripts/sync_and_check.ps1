param(
    [string]$RepoRoot = "",
    [string]$Branch = "",
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

$autoSyncScript = Join-Path $PSScriptRoot "auto_sync.ps1"
$checkScript = Join-Path $PSScriptRoot "check_repo_sync.ps1"

if (-not (Test-Path $autoSyncScript)) {
    throw "Missing script: $autoSyncScript"
}
if (-not (Test-Path $checkScript)) {
    throw "Missing script: $checkScript"
}

& $autoSyncScript -RepoRoot $RepoRoot -Branch $Branch -CommitMessage $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Auto sync failed."
}

& $checkScript -RepoRoot $RepoRoot -Branch $Branch
if ($LASTEXITCODE -ne 0) {
    throw "Sync check failed: local and remote are not identical."
}

Write-Host "[sync-and-check] Repository is fully synchronized."
