param(
    [string]$SourceRepoPath,
    [int]$Port = 18080,
    [int]$DetectTimeoutSeconds = 45,
    [int]$HealthCheckTimeoutSeconds = 30,
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

function Resolve-PublicUrl([string]$OutPath, [string]$ErrPath, [int]$TimeoutSec = 45) {
    function Read-SharedText([string]$PathValue) {
        if (-not (Test-Path $PathValue)) {
            return ""
        }
        $fs = $null
        $sr = $null
        try {
            $fs = [System.IO.File]::Open($PathValue, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
            $sr = New-Object System.IO.StreamReader($fs)
            return $sr.ReadToEnd()
        }
        catch {
            return ""
        }
        finally {
            if ($sr) { $sr.Dispose() }
            if ($fs) { $fs.Dispose() }
        }
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 1000
        foreach ($path in @($OutPath, $ErrPath)) {
            $text = Read-SharedText $path
            if ([string]::IsNullOrWhiteSpace($text)) { continue }
            $lineMatches = [regex]::Matches($text, "tunneled with tls termination,\s*(https?://[^\s,]+)")
            if ($lineMatches.Count -gt 0) {
                $last = $lineMatches[$lineMatches.Count - 1].Groups[1].Value.TrimEnd("/")
                if (-not [string]::IsNullOrWhiteSpace($last)) {
                    return $last
                }
            }
            $matches = [regex]::Matches($text, "https?://[^\s,]+")
            if ($matches.Count -eq 0) { continue }
            $candidates = New-Object System.Collections.Generic.List[string]
            foreach ($m in $matches) {
                $url = $m.Value.TrimEnd("/")
                if (
                    $url -match "localhost\.run" -or
                    $url -match "localhost:3000" -or
                    $url -match "twitter\.com" -or
                    $url -match "localhost_run"
                ) {
                    continue
                }
                $candidates.Add($url) | Out-Null
            }
            if ($candidates.Count -gt 0) {
                return $candidates[$candidates.Count - 1]
            }
        }
    }
    return $null
}

function Wait-PublicUrlHealthy([string]$Url, [int]$TimeoutSec = 30) {
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return $false
    }
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $root = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
            $state = Invoke-WebRequest -Uri ($Url.TrimEnd("/") + "/PUBLIC_REPO_STATE.json") -UseBasicParsing -TimeoutSec 10
            if ($root.StatusCode -ge 200 -and $root.StatusCode -lt 400 -and $state.StatusCode -ge 200 -and $state.StatusCode -lt 400) {
                return $true
            }
        }
        catch {}
        Start-Sleep -Milliseconds 1500
    }
    return $false
}

$sourceRoot = Resolve-SourceRoot
$runtimeDir = Join-Path $sourceRoot "setup_reports"
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
}
$runtimePath = Join-Path $runtimeDir "public_runtime_state.json"
$outPath = Join-Path $runtimeDir "public_tunnel_stdout.log"
$errPath = Join-Path $runtimeDir "public_tunnel_stderr.log"
$previousPublicUrl = $null

# Ensure local web is running first.
$startWebScript = Join-Path $sourceRoot "tools/public_mirror/start_public_mirror_web.ps1"
& $startWebScript -SourceRepoPath $sourceRoot -Port $Port | Out-Null

$state = Read-RuntimeState $runtimePath
$previousPublicUrl = [string]$state["public_url"]
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

# Prevent stale URL extraction from previous tunnel session logs.
Set-Content -Path $outPath -Value "" -Encoding UTF8
Set-Content -Path $errPath -Value "" -Encoding UTF8

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

$publicUrl = Resolve-PublicUrl -OutPath $outPath -ErrPath $errPath -TimeoutSec $DetectTimeoutSeconds
if (-not $publicUrl) {
    if (-not $proc.HasExited) {
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            tunnel_pid = $null
            tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
            public_url = $null
            public_url_status = "NOT_READY"
            previous_public_url = $previousPublicUrl
            public_url_blocker = "No tunnel URL detected from current ssh session output within timeout. External network or tunnel service availability required."
        })
    Write-Host "[public-mirror-public] public URL not ready; blocker recorded in setup_reports/public_runtime_state.json"
    exit 2
}

$healthy = Wait-PublicUrlHealthy -Url $publicUrl -TimeoutSec $HealthCheckTimeoutSeconds
if (-not $healthy) {
    if (-not $proc.HasExited) {
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            tunnel_pid = $null
            tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
            public_url = $publicUrl
            public_url_status = "NOT_READY"
            previous_public_url = $previousPublicUrl
            public_url_blocker = "Tunnel URL detected but failed live health check for root/PUBLIC_REPO_STATE.json."
        })
    Write-Host "[public-mirror-public] URL detected but health check failed: $publicUrl"
    exit 3
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        tunnel_pid = $proc.Id
        tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
        public_url = $publicUrl
        public_url_status = "READY"
        public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        previous_public_url = $previousPublicUrl
        public_url_blocker = $null
    })

Write-Host "[public-mirror-public] ready url=$publicUrl pid=$($proc.Id)"
