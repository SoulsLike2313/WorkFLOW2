param(
    [string]$SourceRepoPath,
    [string]$PublicUrl
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

function Write-RuntimePatch([string]$PathValue, [hashtable]$Patch) {
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

function Probe-Url([string]$Url) {
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20
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

function Get-LatestTunnelUrl([string]$OutPath, [string]$ErrPath, [string]$ProviderName) {
    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($path in @($OutPath, $ErrPath)) {
        $text = Read-SharedText $path
        if ([string]::IsNullOrWhiteSpace($text)) { continue }

        if ($ProviderName -eq "cloudflared_quick_tunnel") {
            $matches = [regex]::Matches($text, "https://[a-z0-9\-]+\.trycloudflare\.com")
            foreach ($m in $matches) {
                $candidates.Add($m.Value.TrimEnd("/")) | Out-Null
            }
        }
        else {
            $lineMatches = [regex]::Matches($text, "tunneled with tls termination,\s*(https?://[^\s,]+)")
            foreach ($m in $lineMatches) {
                $candidates.Add($m.Groups[1].Value.TrimEnd("/")) | Out-Null
            }
        }
    }
    if ($candidates.Count -eq 0) {
        return $null
    }
    return $candidates[$candidates.Count - 1]
}

$sourceRoot = Resolve-SourceRoot
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
$tunnelOutPath = Join-Path $sourceRoot "setup_reports/public_tunnel_stdout.log"
$tunnelErrPath = Join-Path $sourceRoot "setup_reports/public_tunnel_stderr.log"
$runtime = Read-RuntimeState $runtimePath
$provider = if ($runtime.ContainsKey("public_access_provider")) { [string]$runtime["public_access_provider"] } else { "ssh_localhost_run" }
$vpnDependent = if ($runtime.ContainsKey("public_access_vpn_dependent")) {
    [bool]$runtime["public_access_vpn_dependent"]
}
else {
    if ($provider -eq "cloudflared_quick_tunnel" -or $provider -eq "ssh_localhost_run") { $false } else { $true }
}

if ([string]::IsNullOrWhiteSpace($PublicUrl) -and $runtime.ContainsKey("public_url")) {
    $PublicUrl = [string]$runtime["public_url"]
}

$latestTunnelUrl = Get-LatestTunnelUrl -OutPath $tunnelOutPath -ErrPath $tunnelErrPath -ProviderName $provider
$runtimeUrlOutdated = $false
if (-not [string]::IsNullOrWhiteSpace($latestTunnelUrl) -and $latestTunnelUrl -ne $PublicUrl) {
    $probeLatestRoot = Probe-Url $latestTunnelUrl
    $probeLatestState = Probe-Url ($latestTunnelUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json")
    if ($probeLatestRoot.ok -and $probeLatestState.ok) {
        $runtimeUrlOutdated = $true
        $oldUrl = $PublicUrl
        $PublicUrl = $latestTunnelUrl
        Write-RuntimePatch -PathValue $runtimePath -Patch ([ordered]@{
                previous_public_url = $oldUrl
                public_url = $latestTunnelUrl
                public_url_status = "READY"
                public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
            })
        $runtime = Read-RuntimeState $runtimePath
    }
}

$tunnelPid = if ($runtime.ContainsKey("tunnel_pid")) { [int]$runtime["tunnel_pid"] } else { 0 }
$tunnelAlive = $false
if ($tunnelPid -gt 0) {
    $tunnelAlive = [bool](Get-Process -Id $tunnelPid -ErrorAction SilentlyContinue)
}

$result = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $sourceRoot
    public_url = $PublicUrl
    public_access_provider = $provider
    public_access_mechanism = if ($runtime.ContainsKey("public_access_mechanism")) { [string]$runtime["public_access_mechanism"] } else { $provider }
    public_access_vpn_dependent = $vpnDependent
    local_target_url = if ($runtime.ContainsKey("local_url")) { [string]$runtime["local_url"] } else { "http://127.0.0.1:18080/" }
    tunnel_pid = $tunnelPid
    tunnel_process_alive = $tunnelAlive
    old_public_url = if ($runtime.ContainsKey("previous_public_url")) { [string]$runtime["previous_public_url"] } else { $null }
    old_broken_public_url = if ($runtime.ContainsKey("old_broken_public_url")) { [string]$runtime["old_broken_public_url"] } else { $null }
    old_broken_public_url_cause = if ($runtime.ContainsKey("old_broken_public_url_cause")) { [string]$runtime["old_broken_public_url_cause"] } else { $null }
    latest_tunnel_url_from_logs = $latestTunnelUrl
    runtime_url_outdated = $runtimeUrlOutdated
    failure_cause = $null
    status = "FAIL"
    checks = [ordered]@{}
}

if ([string]::IsNullOrWhiteSpace($PublicUrl)) {
    $result.checks["public_url_present"] = [ordered]@{
        pass = $false
        reason = "public_url_missing"
    }
    $result.failure_cause = "public_url_missing_in_runtime_state"
}
else {
    $rootCheck = Probe-Url $PublicUrl
    $stateCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json")
    $gitCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/.git/")
    $envCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/.env")

    $gitBlocked = ($gitCheck.ok -eq $false) -or ($gitCheck.status -ge 400)
    $envBlocked = ($envCheck.ok -eq $false) -or ($envCheck.status -ge 400)
    $vpnIndependentCheck = -not $vpnDependent

    $result.checks["root_access"] = $rootCheck
    $result.checks["state_file_access"] = $stateCheck
    $result.checks["git_path_blocked"] = [ordered]@{ pass = $gitBlocked; probe = $gitCheck }
    $result.checks["env_path_blocked"] = [ordered]@{ pass = $envBlocked; probe = $envCheck }
    $result.checks["vpn_independent"] = [ordered]@{ pass = $vpnIndependentCheck; value = (-not $vpnDependent) }

    $result.status = if ($rootCheck.ok -and $stateCheck.ok -and $gitBlocked -and $envBlocked -and $vpnIndependentCheck) { "PASS" } else { "FAIL" }
    if ($result.status -ne "PASS") {
        if (-not $tunnelAlive) {
            $result.failure_cause = "tunnel_process_not_alive_stale_session_url"
        }
        elseif ($vpnDependent) {
            $result.failure_cause = "public_access_marked_vpn_dependent"
        }
        elseif (($rootCheck.status -eq 503) -or ($stateCheck.status -eq 503)) {
            $result.failure_cause = "tunnel_endpoint_not_mapped_or_session_expired"
        }
        else {
            $result.failure_cause = "public_url_probe_failed"
        }
    }
}

$jsonPath = Join-Path $sourceRoot "setup_reports/public_access_check.json"
$mdPath = Join-Path $sourceRoot "setup_reports/public_access_check.md"
$result | ConvertTo-Json -Depth 12 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Access Check",
    "",
    "- checked_at_utc: $($result.checked_at_utc)",
    "- public_url: $($result.public_url)",
    "- public_access_provider: $($result.public_access_provider)",
    "- public_access_mechanism: $($result.public_access_mechanism)",
    "- public_access_vpn_dependent: $($result.public_access_vpn_dependent)",
    "- local_target_url: $($result.local_target_url)",
    "- tunnel_pid: $($result.tunnel_pid)",
    "- tunnel_process_alive: $($result.tunnel_process_alive)",
    "- old_public_url: $($result.old_public_url)",
    "- old_broken_public_url: $($result.old_broken_public_url)",
    "- old_broken_public_url_cause: $($result.old_broken_public_url_cause)",
    "- latest_tunnel_url_from_logs: $($result.latest_tunnel_url_from_logs)",
    "- runtime_url_outdated: $($result.runtime_url_outdated)",
    "- failure_cause: $($result.failure_cause)",
    "- status: $($result.status)",
    "",
    "## Checks"
)
foreach ($key in $result.checks.Keys) {
    $item = $result.checks[$key]
    $md += ""
    if ($item -is [hashtable] -or $item -is [System.Collections.IDictionary] -or $item.PSObject.Properties.Count -gt 0) {
        $md += "- $key"
        $md += '```json'
        $md += ($item | ConvertTo-Json -Depth 8)
        $md += '```'
    }
    else {
        $md += ("- {0}: {1}" -f $key, $item)
    }
}
Set-Content -Path $mdPath -Value $md -Encoding UTF8

Write-Host "[public-mirror-public] status=$($result.status) public_url=$PublicUrl"
Write-Host "[public-mirror-public] report_json=$jsonPath"
Write-Host "[public-mirror-public] report_md=$mdPath"

if ($result.status -ne "PASS") {
    exit 1
}
