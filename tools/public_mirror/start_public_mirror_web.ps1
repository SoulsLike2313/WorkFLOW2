param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [int]$Port = 18080,
    [string]$BindAddress = "127.0.0.1",
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

function Resolve-SourceRoot {
    if (-not [string]::IsNullOrWhiteSpace($SourceRepoPath)) {
        return (Resolve-Path $SourceRepoPath).Path
    }
    return (Resolve-Path ((git rev-parse --show-toplevel).Trim())).Path
}

function Resolve-RepoName([string]$RepoRoot) {
    $remote = (git -C $RepoRoot remote get-url origin 2>$null)
    if (-not [string]::IsNullOrWhiteSpace($remote)) {
        $leaf = Split-Path $remote -Leaf
        if ($leaf.EndsWith(".git")) {
            return [System.IO.Path]::GetFileNameWithoutExtension($leaf)
        }
        return $leaf
    }
    return [System.IO.Path]::GetFileName($RepoRoot)
}

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Read-RuntimeState([string]$PathValue) {
    if (Test-Path $PathValue) {
        try {
            return (Get-Content -Raw $PathValue | ConvertFrom-Json -AsHashtable)
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

function Test-WebReady([string]$Url, [int]$TimeoutSeconds = 20) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {}
        Start-Sleep -Milliseconds 500
    }
    return $false
}

$sourceRoot = Resolve-SourceRoot
$repoName = Resolve-RepoName $sourceRoot
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}

$sourceRoot = [System.IO.Path]::GetFullPath($sourceRoot).TrimEnd("\")
$mirrorRoot = [System.IO.Path]::GetFullPath($MirrorPath).TrimEnd("\")
if ($mirrorRoot.StartsWith($sourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Mirror path must be outside source repo: $mirrorRoot"
}
if (-not (Test-Path $mirrorRoot)) {
    throw "Mirror path not found: $mirrorRoot"
}

$runtimeDir = Join-Path $sourceRoot "setup_reports"
Ensure-Directory $runtimeDir
$runtimePath = Join-Path $runtimeDir "public_runtime_state.json"
$outLog = Join-Path $runtimeDir "public_server_stdout.log"
$errLog = Join-Path $runtimeDir "public_server_stderr.log"
$localUrl = "http://$BindAddress`:$Port/"

$state = Read-RuntimeState $runtimePath
$existingPid = $state["local_server_pid"]
if ($existingPid) {
    $existingProcess = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
    if ($existingProcess) {
        if ($ForceRestart) {
            Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
        }
        else {
            if (Test-WebReady -Url $localUrl -TimeoutSeconds 3) {
                Write-Host "[public-mirror-web] already running pid=$existingPid url=$localUrl"
                exit 0
            }
            Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
        }
    }
}

$args = @("-m", "http.server", "$Port", "--bind", $BindAddress, "--directory", $mirrorRoot)
$proc = Start-Process -FilePath "python" -ArgumentList $args -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog

$ready = Test-WebReady -Url $localUrl -TimeoutSeconds 15
if (-not $ready) {
    try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
    throw "Local web server failed to start on $localUrl"
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        source_repo_path = $sourceRoot
        mirror_path = $mirrorRoot
        local_server_pid = $proc.Id
        local_server_command = "python -m http.server $Port --bind $BindAddress --directory $mirrorRoot"
        local_server_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        local_url = $localUrl
    })

Write-Host "[public-mirror-web] started pid=$($proc.Id) url=$localUrl mirror=$mirrorRoot"
