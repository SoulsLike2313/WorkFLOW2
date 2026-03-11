param(
    [string]$RepoRoot = "",
    [string]$Branch = "",
    [string]$RemoteName = "origin",
    [string]$OutputPath = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

Set-Location $RepoRoot

$null = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[sync-check] Not a git repository: $RepoRoot"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (git branch --show-current).Trim()
}
if ([string]::IsNullOrWhiteSpace($Branch)) {
    Write-Host "[sync-check] Could not determine branch."
    exit 1
}

git fetch $RemoteName --prune
if ($LASTEXITCODE -ne 0) {
    Write-Host "[sync-check] git fetch failed."
    exit 1
}

$localHead = (git rev-parse HEAD).Trim()
$remoteHead = (git rev-parse "$RemoteName/$Branch").Trim()
$lrCounts = (git rev-list --left-right --count "HEAD...$RemoteName/$Branch").Trim().Split([char]9)
$ahead = [int]$lrCounts[0]
$behind = [int]$lrCounts[1]

$statusLines = git status --porcelain=v1
$hasWorkingChanges = -not [string]::IsNullOrWhiteSpace(($statusLines | Out-String).Trim())
$commitsMatch = $localHead -eq $remoteHead

$overallStatus = if ($commitsMatch -and -not $hasWorkingChanges -and $ahead -eq 0 -and $behind -eq 0) { "PASS" } else { "FAIL" }

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $timestamp = Get-Date -Format "yyyyMMddTHHmmss"
    $outDir = Join-Path $RepoRoot "runtime\sync_checks"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $OutputPath = Join-Path $outDir "sync_check_$timestamp.json"
}

$report = [ordered]@{
    checked_at = (Get-Date).ToString("o")
    repo_root = $RepoRoot
    remote = $RemoteName
    branch = $Branch
    status = $overallStatus
    local_head = $localHead
    remote_head = $remoteHead
    commits_match = $commitsMatch
    ahead = $ahead
    behind = $behind
    working_tree_clean = (-not $hasWorkingChanges)
    has_working_changes = $hasWorkingChanges
    working_changes = @($statusLines)
}

$json = $report | ConvertTo-Json -Depth 6
$outputDir = Split-Path -Parent $OutputPath
if (-not [string]::IsNullOrWhiteSpace($outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}
Set-Content -Path $OutputPath -Value $json -Encoding UTF8

Write-Host "[sync-check] status: $overallStatus"
Write-Host "[sync-check] local:  $localHead"
Write-Host "[sync-check] remote: $remoteHead"
Write-Host "[sync-check] ahead=$ahead behind=$behind clean=$(-not $hasWorkingChanges)"
Write-Host "[sync-check] report: $OutputPath"

if ($overallStatus -eq "PASS") {
    exit 0
}
exit 1
