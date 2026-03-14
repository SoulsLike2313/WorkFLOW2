param(
    [string]$SourceRepoPath
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($SourceRepoPath)) {
    $SourceRepoPath = (git rev-parse --show-toplevel).Trim()
}
else {
    $SourceRepoPath = (Resolve-Path $SourceRepoPath).Path
}

$runtimeStatePath = Join-Path $SourceRepoPath "setup_reports/public_runtime_state.json"
if (-not (Test-Path $runtimeStatePath)) {
    Write-Host "[public-mirror] runtime state not found: $runtimeStatePath"
    exit 0
}

$state = Get-Content -Raw $runtimeStatePath | ConvertFrom-Json
$killed = @()

foreach ($pidField in @("watch_pid", "local_server_pid", "tunnel_pid")) {
    $pidValue = $state.$pidField
    if ($pidValue) {
        try {
            Stop-Process -Id $pidValue -Force -ErrorAction Stop
            $killed += "$pidField=$pidValue"
        }
        catch {}
    }
}

$stateHash = $state | ConvertTo-Json -Depth 8 | ConvertFrom-Json -AsHashtable
$stateHash["watch_mode"] = "stopped"
$stateHash["stopped_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
$stateHash | ConvertTo-Json -Depth 8 | Set-Content -Path $runtimeStatePath -Encoding UTF8

Write-Host "[public-mirror] stopped processes: $($killed -join ', ')"
