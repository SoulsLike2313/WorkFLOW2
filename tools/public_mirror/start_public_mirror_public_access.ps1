param(
    [string]$SourceRepoPath,
    [int]$Port = 18080,
    [int]$DetectTimeoutSeconds = 60,
    [int]$HealthCheckTimeoutSeconds = 45,
    [ValidateSet("cloudflared_quick_tunnel", "ssh_localhost_run")]
    [string]$Provider = "ssh_localhost_run",
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
    $state | ConvertTo-Json -Depth 12 | Set-Content -Path $PathValue -Encoding UTF8
}

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

function Probe-UrlStatus([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return $null
    }
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        return [int]$resp.StatusCode
    }
    catch {
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            return [int]$_.Exception.Response.StatusCode
        }
        return $null
    }
}

function Resolve-PublicUrlFromLogs {
    param(
        [string]$OutPath,
        [string]$ErrPath,
        [string]$ProviderName,
        [int]$TimeoutSec
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 1000
        foreach ($path in @($OutPath, $ErrPath)) {
            $text = Read-SharedText $path
            if ([string]::IsNullOrWhiteSpace($text)) { continue }

            if ($ProviderName -eq "cloudflared_quick_tunnel") {
                $matches = [regex]::Matches($text, "https://[a-z0-9\-]+\.trycloudflare\.com")
                if ($matches.Count -gt 0) {
                    return $matches[$matches.Count - 1].Value.TrimEnd("/")
                }
            }
            else {
                $lineMatches = [regex]::Matches($text, "tunneled with tls termination,\s*(https?://[^\s,]+)")
                if ($lineMatches.Count -gt 0) {
                    return $lineMatches[$lineMatches.Count - 1].Groups[1].Value.TrimEnd("/")
                }
                $genericMatches = [regex]::Matches($text, "https?://[^\s,]+")
                if ($genericMatches.Count -gt 0) {
                    $filtered = New-Object System.Collections.Generic.List[string]
                    foreach ($m in $genericMatches) {
                        $url = $m.Value.TrimEnd("/")
                        if (
                            $url -match "localhost\.run" -or
                            $url -match "localhost:3000" -or
                            $url -match "twitter\.com" -or
                            $url -match "localhost_run"
                        ) {
                            continue
                        }
                        $filtered.Add($url) | Out-Null
                    }
                    if ($filtered.Count -gt 0) {
                        return $filtered[$filtered.Count - 1]
                    }
                }
            }
        }
    }
    return $null
}

function Wait-PublicUrlHealthy([string]$Url, [int]$TimeoutSec = 45) {
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

function Stop-ProcessSafe([int]$PidValue) {
    if ($PidValue -le 0) { return }
    try {
        Stop-Process -Id $PidValue -Force -ErrorAction Stop
    }
    catch {}
}

function Get-ProviderCommand([string]$ProviderName) {
    if ($ProviderName -eq "cloudflared_quick_tunnel") {
        $cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
        foreach ($candidate in @(
                "C:\Program Files\cloudflared\cloudflared.exe",
                "C:\Program Files (x86)\cloudflared\cloudflared.exe"
            )) {
            if (Test-Path $candidate) {
                return $candidate
            }
        }
        return $null
    }
    $ssh = Get-Command ssh -ErrorAction SilentlyContinue
    if ($ssh) { return $ssh.Source }
    return $null
}

function Get-NonVpnBindIPv4 {
    $routes = Get-NetRoute -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
        Sort-Object RouteMetric
    foreach ($route in $routes) {
        $alias = [string]$route.InterfaceAlias
        if ($alias -match "(?i)tun|vpn|warp|wireguard|tailscale|happ") {
            continue
        }
        $ip = Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $route.ifIndex -ErrorAction SilentlyContinue |
            Where-Object { $_.IPAddress -notmatch "^169\.254\." -and $_.PrefixOrigin -ne "WellKnown" } |
            Select-Object -First 1
        if ($ip) {
            return [ordered]@{
                ip = [string]$ip.IPAddress
                interface_alias = $alias
                interface_index = [int]$route.ifIndex
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
& $startWebScript -SourceRepoPath $sourceRoot -Port $Port | Out-Null

$state = Read-RuntimeState $runtimePath
$previousPublicUrl = if ($state.ContainsKey("public_url")) { [string]$state["public_url"] } else { $null }
$previousPid = if ($state.ContainsKey("tunnel_pid")) { [int]$state["tunnel_pid"] } else { 0 }
$oldBrokenUrl = if ($state.ContainsKey("old_broken_public_url")) { [string]$state["old_broken_public_url"] } else { $null }
$oldBrokenCause = if ($state.ContainsKey("old_broken_public_url_cause")) { [string]$state["old_broken_public_url_cause"] } else { $null }

$previousProcessAlive = $false
if ($previousPid -gt 0) {
    $previousProcessAlive = [bool](Get-Process -Id $previousPid -ErrorAction SilentlyContinue)
}
$previousStatus = Probe-UrlStatus -Url $previousPublicUrl
if (-not [string]::IsNullOrWhiteSpace($previousPublicUrl)) {
    if (-not $previousProcessAlive) {
        $oldBrokenUrl = $previousPublicUrl
        $oldBrokenCause = "stale_session_process_not_alive"
    }
    elseif ($null -ne $previousStatus -and $previousStatus -ge 500) {
        $oldBrokenUrl = $previousPublicUrl
        $oldBrokenCause = "stale_session_hostname_not_mapped"
    }
}

if ($previousPid -gt 0 -and ($ForceRestart -or $Provider -ne $state["public_access_provider"])) {
    Stop-ProcessSafe -PidValue $previousPid
}

# Clean logs to avoid stale URL extraction.
Set-Content -Path $outPath -Value "" -Encoding UTF8
Set-Content -Path $errPath -Value "" -Encoding UTF8

$providerCommand = Get-ProviderCommand -ProviderName $Provider
if ([string]::IsNullOrWhiteSpace($providerCommand)) {
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            public_access_provider = $Provider
            public_access_mechanism = if ($Provider -eq "cloudflared_quick_tunnel") { "cloudflared quick tunnel (trycloudflare.com)" } else { "ssh reverse tunnel via localhost.run" }
            public_access_vpn_dependent = ($Provider -ne "cloudflared_quick_tunnel")
            tunnel_pid = $null
            public_url = $null
            public_url_status = "NOT_READY"
            previous_public_url = $previousPublicUrl
            old_broken_public_url = $oldBrokenUrl
            old_broken_public_url_cause = $oldBrokenCause
            public_url_blocker = "provider_binary_not_found"
        })
    Write-Host "[public-mirror-public] provider executable not found for $Provider"
    exit 4
}

if ($Provider -eq "cloudflared_quick_tunnel") {
    $args = @("tunnel", "--url", "http://127.0.0.1:$Port", "--no-autoupdate", "--protocol", "http2")
    $publicAccessMechanism = "cloudflared quick tunnel (trycloudflare.com)"
    $vpnDependent = $false
    $bindInfo = $null
}
else {
    $bindInfo = Get-NonVpnBindIPv4
    if ($null -eq $bindInfo -or [string]::IsNullOrWhiteSpace($bindInfo.ip)) {
        Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
                public_access_provider = $Provider
                public_access_mechanism = "ssh reverse tunnel via localhost.run (direct route bind unavailable)"
                public_access_vpn_dependent = $true
                tunnel_pid = $null
                public_url = $null
                public_url_status = "NOT_READY"
                previous_public_url = $previousPublicUrl
                old_broken_public_url = $oldBrokenUrl
                old_broken_public_url_cause = $oldBrokenCause
                public_url_blocker = "no_non_vpn_ipv4_interface_found_for_ssh_bind"
            })
        Write-Host "[public-mirror-public] unable to find non-VPN IPv4 interface for SSH bind"
        exit 5
    }
    $args = @(
        "-4",
        "-b", [string]$bindInfo.ip,
        "-o", "ExitOnForwardFailure=yes",
        "-o", "TCPKeepAlive=yes",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=2",
        "-o", "ConnectTimeout=15",
        "-o", "ConnectionAttempts=3",
        "-o", "IPQoS=none",
        "-o", "LogLevel=ERROR",
        "-o", "StrictHostKeyChecking=accept-new",
        "-R", "80:127.0.0.1:$Port",
        "nokey@localhost.run"
    )
    $publicAccessMechanism = "ssh reverse tunnel via localhost.run (bound to non-VPN interface)"
    $vpnDependent = $false
}

$proc = Start-Process -FilePath $providerCommand -ArgumentList $args -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $outPath -RedirectStandardError $errPath

$publicUrl = Resolve-PublicUrlFromLogs -OutPath $outPath -ErrPath $errPath -ProviderName $Provider -TimeoutSec $DetectTimeoutSeconds
if ([string]::IsNullOrWhiteSpace($publicUrl)) {
    if (-not $proc.HasExited) {
        Stop-ProcessSafe -PidValue $proc.Id
    }
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            public_access_provider = $Provider
            public_access_mechanism = $publicAccessMechanism
            public_access_vpn_dependent = $vpnDependent
            tunnel_pid = $null
            tunnel_command = "$providerCommand $($args -join ' ')"
            public_url = $null
            public_url_status = "NOT_READY"
            previous_public_url = $previousPublicUrl
            old_broken_public_url = $oldBrokenUrl
            old_broken_public_url_cause = $oldBrokenCause
            public_url_blocker = "public_url_not_detected_from_current_session_logs"
            bound_interface_alias = if ($bindInfo) { [string]$bindInfo.interface_alias } else { $null }
            bound_interface_ip = if ($bindInfo) { [string]$bindInfo.ip } else { $null }
        })
    Write-Host "[public-mirror-public] URL detection failed for provider=$Provider"
    exit 2
}

$healthy = Wait-PublicUrlHealthy -Url $publicUrl -TimeoutSec $HealthCheckTimeoutSeconds
if (-not $healthy) {
    if (-not $proc.HasExited) {
        Stop-ProcessSafe -PidValue $proc.Id
    }
    Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
            public_access_provider = $Provider
            public_access_mechanism = $publicAccessMechanism
            public_access_vpn_dependent = $vpnDependent
            tunnel_pid = $null
            tunnel_command = "$providerCommand $($args -join ' ')"
            public_url = $publicUrl
            public_url_status = "NOT_READY"
            previous_public_url = $previousPublicUrl
            old_broken_public_url = $oldBrokenUrl
            old_broken_public_url_cause = $oldBrokenCause
            public_url_blocker = "public_url_failed_live_health_check"
            bound_interface_alias = if ($bindInfo) { [string]$bindInfo.interface_alias } else { $null }
            bound_interface_ip = if ($bindInfo) { [string]$bindInfo.ip } else { $null }
        })
    Write-Host "[public-mirror-public] URL health check failed: $publicUrl"
    exit 3
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        public_access_provider = $Provider
        public_access_mechanism = $publicAccessMechanism
        public_access_vpn_dependent = $vpnDependent
        tunnel_pid = $proc.Id
        tunnel_command = "$providerCommand $($args -join ' ')"
        tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        local_url = "http://127.0.0.1:$Port/"
        public_url = $publicUrl
        public_url_status = "READY"
        public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        previous_public_url = $previousPublicUrl
        old_broken_public_url = $oldBrokenUrl
        old_broken_public_url_cause = $oldBrokenCause
        public_url_blocker = $null
        bound_interface_alias = if ($bindInfo) { [string]$bindInfo.interface_alias } else { $null }
        bound_interface_ip = if ($bindInfo) { [string]$bindInfo.ip } else { $null }
    })

Write-Host "[public-mirror-public] ready provider=$Provider url=$publicUrl pid=$($proc.Id)"
