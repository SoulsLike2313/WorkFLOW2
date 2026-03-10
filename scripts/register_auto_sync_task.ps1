param(
    [string]$TaskName = "CVVCODEX_AutoSync",
    [int]$Minutes = 15
)

$ErrorActionPreference = "Stop"

if ($Minutes -lt 1) {
    throw "Minutes must be >= 1"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$syncScript = Join-Path $PSScriptRoot "auto_sync.ps1"
$branch = (git -C $repoRoot branch --show-current).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
}

$command = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$syncScript`" -RepoRoot `"$repoRoot`" -Branch `"$branch`""

schtasks /Create /F /SC MINUTE /MO $Minutes /TN $TaskName /TR $command | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create scheduled task."
}

Write-Host "Auto-sync task created."
Write-Host "TaskName: $TaskName"
Write-Host "Interval: every $Minutes minute(s)"
Write-Host "Command: $command"
