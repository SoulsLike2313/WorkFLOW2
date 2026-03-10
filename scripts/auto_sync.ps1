param(
    [string]$RepoRoot = "",
    [string]$Branch = "",
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

Set-Location $RepoRoot

$null = git rev-parse --is-inside-work-tree 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] Not a git repository: $RepoRoot"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Branch)) {
    $Branch = (git branch --show-current).Trim()
}
if ([string]::IsNullOrWhiteSpace($Branch)) {
    Write-Host "[auto-sync] Could not determine branch."
    exit 1
}

Write-Host "[auto-sync] Repository: $RepoRoot"
Write-Host "[auto-sync] Branch: $Branch"

git fetch origin
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] git fetch failed."
    exit 1
}

git pull --rebase --autostash origin $Branch
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] git pull --rebase failed. Manual intervention may be required."
    exit 1
}

$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace(($status | Out-String).Trim())) {
    Write-Host "[auto-sync] No local changes."
    exit 0
}

git add -A
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] git add failed."
    exit 1
}

git diff --cached --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "[auto-sync] No staged changes after add."
    exit 0
}

if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    $CommitMessage = "auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
}

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] git commit failed."
    exit 1
}

git push origin $Branch
if ($LASTEXITCODE -ne 0) {
    Write-Host "[auto-sync] git push failed."
    exit 1
}

Write-Host "[auto-sync] Push completed."
