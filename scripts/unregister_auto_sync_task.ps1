param(
    [string]$TaskName = "CVVCODEX_AutoSync"
)

$ErrorActionPreference = "Stop"

schtasks /Delete /F /TN $TaskName | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to delete scheduled task '$TaskName'."
}

Write-Host "Auto-sync task removed: $TaskName"
