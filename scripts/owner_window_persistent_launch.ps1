param(
    [string]$ConfigPath = "runtime/factory_observation/owner_window_persistent_runtime_config_v1.json",
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Resolve-RepoPath {
    param([string]$PathValue)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ""
    }
    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $repoRoot $PathValue))
}

function Test-OwnerWindowEndpoint {
    param(
        [string]$BindHost,
        [int]$Port
    )
    try {
        $uri = "http://$BindHost`:$Port/api/state"
        $resp = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 3
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Get-OwnerWindowProcesses {
    return @(Get-CimInstance Win32_Process | Where-Object {
            $_.CommandLine -and $_.CommandLine -match "local_factory_observation_server\.py"
        })
}

function Get-ListeningPidByPort {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -eq $conn) {
            return $null
        }
        return [int]$conn.OwningProcess
    } catch {
        return $null
    }
}

function Write-RuntimeStatus {
    param(
        [hashtable]$Base,
        [string]$StatusPath
    )
    $dir = Split-Path -Parent $StatusPath
    if (-not [string]::IsNullOrWhiteSpace($dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    ($Base | ConvertTo-Json -Depth 8) | Set-Content -Path $StatusPath -Encoding UTF8
}

function Rotate-LogFile {
    param([string]$PathValue)
    if (-not (Test-Path -LiteralPath $PathValue)) {
        return
    }
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $backup = "$PathValue.$stamp.bak"
    Copy-Item -LiteralPath $PathValue -Destination $backup -Force
}

$configFullPath = Resolve-RepoPath $ConfigPath
if (-not (Test-Path -LiteralPath $configFullPath)) {
    throw "Owner window runtime config not found: $configFullPath"
}

$config = Get-Content -Path $configFullPath -Raw -Encoding UTF8 | ConvertFrom-Json

$bindHost = if ($config.host) { [string]$config.host } else { "127.0.0.1" }
$preferredPort = if ($config.preferred_port) { [int]$config.preferred_port } else { 8777 }
$fallbackPorts = @()
if ($config.port_fallback_range) {
    foreach ($port in $config.port_fallback_range) {
        $fallbackPorts += [int]$port
    }
}

$taskName = if ($config.task_name) { [string]$config.task_name } else { "CVVCODEX_OwnerWindow_Localhost_Autostart_V1" }
$pythonExecutableRaw = if ($config.python_executable) { [string]$config.python_executable } else { "python" }
$pythonCommand = $pythonExecutableRaw
if (-not [System.IO.Path]::IsPathRooted($pythonExecutableRaw)) {
    try {
        $resolvedPython = (Get-Command $pythonExecutableRaw -ErrorAction Stop).Source
        if ($resolvedPython) {
            $pythonCommand = $resolvedPython
        }
    } catch {
        $pythonCommand = $pythonExecutableRaw
    }
}

$serverScriptPath = Resolve-RepoPath ([string]$config.server_script_path)
if (-not (Test-Path -LiteralPath $serverScriptPath)) {
    throw "Owner window server entrypoint not found: $serverScriptPath"
}

$bundlePath = Resolve-RepoPath ([string]$config.bundle_path)
$bundleSource = "primary_bundle"
if (-not (Test-Path -LiteralPath $bundlePath)) {
    $fallbackBundle = Resolve-RepoPath ([string]$config.fallback_bundle_path)
    if ([string]::IsNullOrWhiteSpace($fallbackBundle) -or -not (Test-Path -LiteralPath $fallbackBundle)) {
        throw "Primary bundle missing and fallback missing. Primary: $bundlePath ; Fallback: $fallbackBundle"
    }
    $bundlePath = $fallbackBundle
    $bundleSource = "fallback_bundle"
}

$companionBundlePath = Resolve-RepoPath ([string]$config.companion_bundle_path)
$liveEventLogPath = Resolve-RepoPath ([string]$config.live_event_log_path)
$liveSnapshotPath = Resolve-RepoPath ([string]$config.live_snapshot_path)
$stdoutLogPath = Resolve-RepoPath ([string]$config.stdout_log_path)
$stderrLogPath = Resolve-RepoPath ([string]$config.stderr_log_path)
$runtimeStatusPath = Resolve-RepoPath ([string]$config.runtime_status_path)
$persistLiveSnapshot = [bool]$config.persist_live_snapshot
$startupTimeoutSeconds = if ($config.startup_timeout_seconds) { [int]$config.startup_timeout_seconds } else { 20 }

foreach ($pathValue in @($liveEventLogPath, $liveSnapshotPath, $stdoutLogPath, $stderrLogPath, $runtimeStatusPath)) {
    $dir = Split-Path -Parent $pathValue
    if (-not [string]::IsNullOrWhiteSpace($dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

$candidatePorts = @($preferredPort) + $fallbackPorts | Select-Object -Unique
$selectedPort = $null
$reusedPid = $null

foreach ($port in $candidatePorts) {
    $healthy = Test-OwnerWindowEndpoint -BindHost $bindHost -Port $port
    $listeningPid = Get-ListeningPidByPort -Port $port
    $ownerProcess = $null
    if ($null -ne $listeningPid) {
        $ownerProcess = Get-OwnerWindowProcesses | Where-Object { $_.ProcessId -eq $listeningPid } | Select-Object -First 1
    }

    if ($healthy -and -not $ForceRestart.IsPresent) {
        $selectedPort = $port
        $reusedPid = if ($null -ne $listeningPid) { [int]$listeningPid } else { 0 }
        break
    }

    if ($null -eq $listeningPid) {
        $selectedPort = $port
        break
    }

    if ($ownerProcess) {
        if ($ForceRestart.IsPresent -or -not $healthy) {
            Stop-Process -Id $listeningPid -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            if ($null -eq (Get-ListeningPidByPort -Port $port)) {
                $selectedPort = $port
                break
            }
        }
        continue
    }
}

if ($null -eq $selectedPort) {
    foreach ($port in 8783..8799) {
        if ($null -eq (Get-ListeningPidByPort -Port $port)) {
            $selectedPort = $port
            break
        }
    }
}

if ($null -eq $selectedPort) {
    throw "No free localhost port found for owner window runtime."
}

$statusBase = [ordered]@{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    task_name = $taskName
    host = $bindHost
    port = [int]$selectedPort
    url = "http://$bindHost`:$selectedPort/?mode=fullvision"
    bundle_path = $bundlePath
    bundle_source = $bundleSource
    companion_bundle_path = $companionBundlePath
    live_event_log_path = $liveEventLogPath
    live_snapshot_path = $liveSnapshotPath
    stdout_log_path = $stdoutLogPath
    stderr_log_path = $stderrLogPath
    force_restart = [bool]$ForceRestart.IsPresent
}

if ($reusedPid -and $reusedPid -gt 0) {
    $statusBase.launch_mode = "REUSED_EXISTING_HEALTHY_RUNTIME"
    $statusBase.pid = [int]$reusedPid
    $statusBase.healthy = $true
    $statusBase.note = "Existing owner window runtime already healthy; duplicate launch skipped."
    Write-RuntimeStatus -Base $statusBase -StatusPath $runtimeStatusPath
    Write-Output "REUSED http://$bindHost`:$selectedPort PID=$reusedPid"
    exit 0
}

Rotate-LogFile -PathValue $stdoutLogPath
Rotate-LogFile -PathValue $stderrLogPath

$argList = @(
    "-u",
    $serverScriptPath,
    "--bundle", $bundlePath,
    "--host", $bindHost,
    "--port", "$selectedPort",
    "--live-event-log", $liveEventLogPath,
    "--live-snapshot-path", $liveSnapshotPath
)
if ($persistLiveSnapshot) {
    $argList += "--persist-live-snapshot"
}

$proc = Start-Process `
    -FilePath $pythonCommand `
    -ArgumentList $argList `
    -WorkingDirectory $repoRoot `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutLogPath `
    -RedirectStandardError $stderrLogPath

$deadline = (Get-Date).AddSeconds($startupTimeoutSeconds)
$healthyAfterStart = $false
while ((Get-Date) -lt $deadline) {
    if (Test-OwnerWindowEndpoint -BindHost $bindHost -Port $selectedPort) {
        $healthyAfterStart = $true
        break
    }
    Start-Sleep -Seconds 1
}

$statusBase.pid = [int]$proc.Id
$statusBase.command = "$pythonCommand $($argList -join ' ')"
$statusBase.healthy = [bool]$healthyAfterStart

if (-not $healthyAfterStart) {
    $statusBase.launch_mode = "FAILED_TO_REACH_HEALTH_ENDPOINT"
    $statusBase.note = "Process started but /api/state did not become healthy before timeout."
    Write-RuntimeStatus -Base $statusBase -StatusPath $runtimeStatusPath
    throw "Owner window runtime failed health check after launch. Check logs: $stdoutLogPath ; $stderrLogPath"
}

$statusBase.launch_mode = "STARTED_NEW_RUNTIME"
$statusBase.note = "Owner window runtime launched by persistent wrapper."
Write-RuntimeStatus -Base $statusBase -StatusPath $runtimeStatusPath
Write-Output "STARTED http://$bindHost`:$selectedPort PID=$($proc.Id)"
