param(
    [string]$SourceRepoPath,
    [string]$CanonicalHostname,
    [string]$PublicScheme = "http",
    [int]$PublicPort = 18080,
    [switch]$AllowExternalIpFallback = $true,
    [switch]$StopLegacyTunnel = $true
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

function Probe-Url([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return [ordered]@{ ok = $false; status = $null; error = "empty_url" }
    }
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 12
        return [ordered]@{ ok = $true; status = [int]$resp.StatusCode; error = $null }
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        return [ordered]@{ ok = $false; status = $statusCode; error = $_.Exception.Message }
    }
}

function Get-NetworkSnapshot {
    $route = Get-NetRoute -AddressFamily IPv4 -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue |
        Sort-Object RouteMetric |
        Select-Object -First 1
    $ip = $null
    if ($route) {
        $ip = Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $route.ifIndex -ErrorAction SilentlyContinue |
            Where-Object { $_.IPAddress -notmatch "^169\.254\." } |
            Select-Object -First 1
    }
    $externalIp = $null
    try {
        $externalIp = (Invoke-RestMethod -Uri "https://api.ipify.org?format=json" -TimeoutSec 10).ip
    }
    catch {}
    return [ordered]@{
        interface_alias = if ($route) { [string]$route.InterfaceAlias } else { $null }
        local_ip = if ($ip) { [string]$ip.IPAddress } else { $null }
        gateway = if ($route) { [string]$route.NextHop } else { $null }
        external_ip = $externalIp
    }
}

$sourceRoot = Resolve-SourceRoot
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
$runtime = Read-RuntimeState $runtimePath

if ([string]::IsNullOrWhiteSpace($CanonicalHostname)) {
    if ($runtime.ContainsKey("canonical_public_hostname") -and -not [string]::IsNullOrWhiteSpace([string]$runtime["canonical_public_hostname"])) {
        $CanonicalHostname = [string]$runtime["canonical_public_hostname"]
    }
    elseif (-not [string]::IsNullOrWhiteSpace($env:PUBLIC_MIRROR_HOSTNAME)) {
        $CanonicalHostname = [string]$env:PUBLIC_MIRROR_HOSTNAME
    }
}

$startWebScript = Join-Path $sourceRoot "tools/public_mirror/start_public_mirror_web.ps1"
& $startWebScript -SourceRepoPath $sourceRoot | Out-Null

$runtime = Read-RuntimeState $runtimePath
$localUrl = if ($runtime.ContainsKey("local_url")) { [string]$runtime["local_url"] } else { "http://127.0.0.1:18080/" }

if ($StopLegacyTunnel -and $runtime.ContainsKey("tunnel_pid") -and $runtime["tunnel_pid"]) {
    $legacyPid = [int]$runtime["tunnel_pid"]
    $legacyProc = Get-Process -Id $legacyPid -ErrorAction SilentlyContinue
    if ($legacyProc) {
        try { Stop-Process -Id $legacyPid -Force -ErrorAction Stop } catch {}
    }
}

$network = Get-NetworkSnapshot
$localProbe = Probe-Url -Url $localUrl

$publicUrl = $null
if ([string]::IsNullOrWhiteSpace($CanonicalHostname) -and $AllowExternalIpFallback -and -not [string]::IsNullOrWhiteSpace([string]$network.external_ip)) {
    $CanonicalHostname = [string]$network.external_ip
}

if (-not [string]::IsNullOrWhiteSpace($CanonicalHostname)) {
    if (($PublicScheme -eq "http" -and $PublicPort -eq 80) -or ($PublicScheme -eq "https" -and $PublicPort -eq 443)) {
        $publicUrl = "${PublicScheme}://$CanonicalHostname"
    }
    else {
        $publicUrl = "${PublicScheme}://$CanonicalHostname`:$PublicPort"
    }
}

$publicProbe = Probe-Url -Url $publicUrl
$status = "NOT_READY"
$blocker = $null
if (-not $localProbe.ok) {
    $blocker = "canonical_local_caddy_web_not_reachable"
}
elseif ([string]::IsNullOrWhiteSpace($CanonicalHostname)) {
    $blocker = "router_port_forwarding_or_dns_mapping_not_configured"
}
elseif (-not $publicProbe.ok) {
    $blocker = "router_port_forwarding_or_dns_mapping_not_configured"
}
else {
    $status = "READY"
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        source_repo_path = $sourceRoot
        public_access_provider = "direct_local_pc_caddy"
        public_access_mechanism = "direct local-PC hosting via Caddy (non-tunnel canonical)"
        public_access_vpn_dependent = $false
        public_access_session_based = $false
        public_access_one_external_blocker = if ($status -eq "READY") { $null } else { $blocker }
        public_url = $publicUrl
        public_url_status = $status
        public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        public_url_blocker = if ($status -eq "READY") { $null } else { $blocker }
        local_url = $localUrl
        canonical_public_hostname = $CanonicalHostname
        canonical_public_scheme = $PublicScheme
        canonical_public_port = $PublicPort
        ddns_domain_status = if ([string]::IsNullOrWhiteSpace($CanonicalHostname)) { "not_configured" } elseif ($CanonicalHostname -eq [string]$network.external_ip) { "external_ip_literal_fallback" } else { "configured" }
        router_port_forwarding_configured = ($status -eq "READY")
        direct_hosting_network = $network
        tunnel_pid = $null
        tunnel_command = $null
    })

Write-Host "[public-mirror-public] provider=direct_local_pc_caddy local_url=$localUrl"
if ($status -eq "READY") {
    Write-Host "[public-mirror-public] public_url_ready=$publicUrl"
}
else {
    Write-Host "[public-mirror-public] public_url_not_ready blocker=$blocker"
}
