param(
    [string]$SourceRepoPath
)

$ErrorActionPreference = "Stop"

function Resolve-SourceRoot {
    if (-not [string]::IsNullOrWhiteSpace($SourceRepoPath)) {
        return (Resolve-Path $SourceRepoPath).Path
    }
    return (Resolve-Path ((git rev-parse --show-toplevel).Trim())).Path
}

function Read-RuntimeState([string]$PathValue) {
    if (Test-Path $PathValue) {
        try {
            $obj = Get-Content -Raw $PathValue | ConvertFrom-Json
            $hash = @{}
            if ($obj -ne $null) {
                foreach ($prop in $obj.PSObject.Properties) {
                    $hash[$prop.Name] = $prop.Value
                }
            }
            return $hash
        }
        catch {}
    }
    return @{}
}

function Write-RuntimeState([string]$PathValue, [hashtable]$Patch) {
    $state = Read-RuntimeState $PathValue
    foreach ($k in $Patch.Keys) {
        $state[$k] = $Patch[$k]
    }
    $state["updated_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
    $state | ConvertTo-Json -Depth 10 | Set-Content -Path $PathValue -Encoding UTF8
}

$sourceRoot = Resolve-SourceRoot
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"

if (-not (Test-Path $runtimePath)) {
    Write-Host "[public-mirror-web] runtime state not found"
    exit 0
}

$state = Read-RuntimeState $runtimePath
$pidValue = $state["local_server_pid"]
$stopped = $false
if ($pidValue) {
    try {
        Stop-Process -Id $pidValue -Force -ErrorAction Stop
        $stopped = $true
    }
    catch {}
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        local_server_pid = $null
        local_server_stopped_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    })

Write-Host "[public-mirror-web] stopped=$stopped pid=$pidValue"
