param(
    [string]$SourceRepoPath,
    [int]$Port = 18080,
    [switch]$ForceRestart
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
        try { return (Get-Content -Raw $PathValue | ConvertFrom-Json -AsHashtable) } catch {}
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

function Resolve-PublicUrl([string]$OutPath, [string]$ErrPath, [int]$TimeoutSec = 45) {
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 1000
        foreach ($path in @($OutPath, $ErrPath)) {
            if (-not (Test-Path $path)) { continue }
            $text = Get-Content -Raw $path -ErrorAction SilentlyContinue
            $match = [regex]::Match($text, "https?://[a-zA-Z0-9\.\-/_]+")
            if ($match.Success) {
                return $match.Value.TrimEnd("/")
            }
        }
    }
    return $null
}

$sourceRoot = Resolve-SourceRoot
$runtimeDir = Join-Path $sourceRoot "setup_reports"
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
}
$runtimePath = Join-Path $runtimeDir "public_runtime_state.json"
$outPath = Join-Path $runtimeDir "public_tunnel_stdout.log"
$errPath = Join-Path $runtimeDir "public_tunnel_stderr.log"

# Ensure local web is running first.
$startWebScript = Join-Path $sourceRoot "tools/public_mirror/start_public_mirror_web.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File $startWebScript -SourceRepoPath $sourceRoot -Port $Port | Out-Null

$state = Read-RuntimeState $runtimePath
$existingPid = $state["tunnel_pid"]
if ($existingPid) {
    $existing = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
    if ($existing) {
        if ($ForceRestart) {
            Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
        }
        elseif ($state.ContainsKey("public_url") -and -not [string]::IsNullOrWhiteSpace([string]$state["public_url"])) {
            Write-Host "[public-mirror-public] already running pid=$existingPid url=$($state["public_url"])"
            exit 0
        }
        else {
            Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
        }
    }
}

$sshArgs = @(
    "-o", "ExitOnForwardFailure=yes",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=3",
    "-o", "StrictHostKeyChecking=accept-new",
    "-R", "80:127.0.0.1:$Port",
    "nokey@localhost.run"
)

$proc = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $outPath -RedirectStandardError $errPath

$publicUrl = Resolve-PublicUrl -OutPath $outPath -ErrPath $errPath -TimeoutSec 45
if (-not $publicUrl) {
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            tunnel_pid = $proc.Id
            tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
            public_url = $null
            public_url_status = "NOT_READY"
            public_url_blocker = "No tunnel URL detected from ssh output. External network/ssh tunnel availability required."
        })
    Write-Host "[public-mirror-public] public URL not ready; blocker recorded in setup_reports/public_runtime_state.json"
    exit 2
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        tunnel_pid = $proc.Id
        tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
        public_url = $publicUrl
        public_url_status = "READY"
        public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        public_url_blocker = $null
    })

Write-Host "[public-mirror-public] ready url=$publicUrl pid=$($proc.Id)"
