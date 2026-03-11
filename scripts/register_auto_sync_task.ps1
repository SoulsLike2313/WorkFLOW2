param(
    [string]$TaskName = "CVVCODEX_AutoSync",
    [int]$Minutes = 15
)

$ErrorActionPreference = "Stop"

if ($Minutes -lt 1) {
    throw "Minutes must be >= 1"
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$hiddenLauncher = Join-Path $PSScriptRoot "auto_sync_hidden.vbs"
$branch = (git -C $repoRoot branch --show-current).Trim()
if ([string]::IsNullOrWhiteSpace($branch)) {
    $branch = "main"
}

if (-not (Test-Path $hiddenLauncher)) {
    throw "Missing launcher: $hiddenLauncher"
}

$command = "wscript.exe //B //NoLogo `"$hiddenLauncher`" `"$repoRoot`" `"$branch`""

schtasks /Create /F /SC MINUTE /MO $Minutes /TN $TaskName /TR $command | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create scheduled task."
}

Write-Host "Auto-sync task created."
Write-Host "TaskName: $TaskName"
Write-Host "Interval: every $Minutes minute(s)"
Write-Host "Command: $command"
