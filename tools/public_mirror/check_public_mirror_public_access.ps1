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

function Probe-Url([string]$Url) {
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20
        return [ordered]@{ ok = $true; status = $resp.StatusCode; error = $null }
    }
    catch {
        $statusCode = $null
        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $statusCode = [int]$_.Exception.Response.StatusCode
        }
        return [ordered]@{ ok = $false; status = $statusCode; error = $_.Exception.Message }
    }
}

$sourceRoot = Resolve-SourceRoot
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
$runtime = Read-RuntimeState $runtimePath
if ([string]::IsNullOrWhiteSpace($PublicUrl) -and $runtime.ContainsKey("public_url")) {
    $PublicUrl = [string]$runtime["public_url"]
}

$result = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $sourceRoot
    public_url = $PublicUrl
    public_access_mechanism = "ssh reverse tunnel via localhost.run"
    local_target_url = if ($runtime.ContainsKey("local_url")) { [string]$runtime["local_url"] } else { "http://127.0.0.1:18080/" }
    tunnel_pid = if ($runtime.ContainsKey("tunnel_pid")) { $runtime["tunnel_pid"] } else { $null }
    tunnel_process_alive = $false
    old_public_url = if ($runtime.ContainsKey("previous_public_url")) { [string]$runtime["previous_public_url"] } else { $null }
    old_broken_public_url = if ($runtime.ContainsKey("old_broken_public_url")) { [string]$runtime["old_broken_public_url"] } else { $null }
    old_broken_public_url_cause = if ($runtime.ContainsKey("old_broken_public_url_cause")) { [string]$runtime["old_broken_public_url_cause"] } else { $null }
    failure_cause = $null
    status = "FAIL"
    checks = [ordered]@{}
}

if ($result.tunnel_pid) {
    $tp = Get-Process -Id $result.tunnel_pid -ErrorAction SilentlyContinue
    $result.tunnel_process_alive = [bool]$tp
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

    $result.checks["root_access"] = $rootCheck
    $result.checks["state_file_access"] = $stateCheck
    $result.checks["git_path_blocked"] = [ordered]@{ pass = $gitBlocked; probe = $gitCheck }
    $result.checks["env_path_blocked"] = [ordered]@{ pass = $envBlocked; probe = $envCheck }
    $result.status = if ($rootCheck.ok -and $stateCheck.ok -and $gitBlocked -and $envBlocked) { "PASS" } else { "FAIL" }
    if ($result.status -ne "PASS") {
        if (-not $result.tunnel_process_alive) {
            $result.failure_cause = "tunnel_process_not_alive_stale_session_url"
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
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Access Check",
    "",
    "- checked_at_utc: $($result.checked_at_utc)",
    "- public_url: $($result.public_url)",
    "- public_access_mechanism: $($result.public_access_mechanism)",
    "- local_target_url: $($result.local_target_url)",
    "- tunnel_pid: $($result.tunnel_pid)",
    "- tunnel_process_alive: $($result.tunnel_process_alive)",
    "- old_public_url: $($result.old_public_url)",
    "- old_broken_public_url: $($result.old_broken_public_url)",
    "- old_broken_public_url_cause: $($result.old_broken_public_url_cause)",
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
