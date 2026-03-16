param(
    [switch]$SkipSafeStateRefresh
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

if (-not (Test-Path (Join-Path $repoRoot "workspace_config\\workspace_manifest.json"))) {
    throw "workspace_config/workspace_manifest.json not found. Repo root not resolved: $repoRoot"
}

Set-Location $repoRoot

if (-not $SkipSafeStateRefresh) {
    python .\scripts\build_safe_mirror_manifest.py --repo-root $repoRoot | Out-Host
}

$status = git status --porcelain
if (-not [string]::IsNullOrWhiteSpace($status)) {
    throw "Working tree is not clean. Commit changes before pushing safe mirror."
}

git push safe_mirror main

$head = git rev-parse HEAD
$remoteMain = git rev-parse safe_mirror/main

Write-Output "safe_mirror push complete."
Write-Output "local_head:  $head"
Write-Output "remote_head: $remoteMain"
