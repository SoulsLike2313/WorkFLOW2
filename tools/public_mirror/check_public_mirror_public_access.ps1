param(
    [string]$SourceRepoPath,
    [string]$PublicUrl,
    [switch]$RunStabilitySeries,
    [int]$RootCheckCount = 10,
    [int]$FileCheckRounds = 5,
    [int]$IntervalSeconds = 6
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

function Probe-Url([string]$Url) {
    if ([string]::IsNullOrWhiteSpace($Url)) {
        return [ordered]@{ ok = $false; status = $null; error = "empty_url" }
    }
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 20 -DisableKeepAlive -Headers @{
            "Cache-Control" = "no-cache"
            Pragma = "no-cache"
        }
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

function Probe-UrlDetailed([string]$Url) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $probe = Probe-Url -Url $Url
    $sw.Stop()
    $probe["checked_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
    $probe["latency_ms"] = [math]::Round($sw.Elapsed.TotalMilliseconds, 2)
    $probe["url"] = $Url
    return $probe
}

function Run-StabilitySeries {
    param(
        [string]$TargetUrl,
        [int]$RootChecks,
        [int]$FileRounds,
        [int]$SleepSeconds
    )

    $result = [ordered]@{
        enabled = $true
        started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        root_checks_requested = $RootChecks
        file_rounds_requested = $FileRounds
        interval_seconds = $SleepSeconds
        root_checks = @()
        file_checks = [ordered]@{
            "/PUBLIC_REPO_STATE.json" = @()
            "/PUBLIC_SYNC_STATUS.json" = @()
            "/PUBLIC_ENTRYPOINTS.md" = @()
        }
        successful_checks = 0
        failed_checks = 0
        total_checks = 0
        success_rate_percent = 0
        classification = "BROKEN"
        stable_enough_for_chatgpt = $false
        session_based_url = $false
    }

    for ($i = 1; $i -le $RootChecks; $i++) {
        $probe = Probe-UrlDetailed -Url $TargetUrl
        $probe["attempt"] = $i
        $result.root_checks += $probe
        $result.total_checks++
        if ($probe.ok) { $result.successful_checks++ } else { $result.failed_checks++ }
        if ($i -lt $RootChecks -and $SleepSeconds -gt 0) {
            Start-Sleep -Seconds $SleepSeconds
        }
    }

    $paths = @("/PUBLIC_REPO_STATE.json", "/PUBLIC_SYNC_STATUS.json", "/PUBLIC_ENTRYPOINTS.md")
    for ($round = 1; $round -le $FileRounds; $round++) {
        foreach ($path in $paths) {
            $probe = Probe-UrlDetailed -Url ($TargetUrl.TrimEnd("/") + $path)
            $probe["round"] = $round
            $probe["path"] = $path
            $result.file_checks[$path] += $probe
            $result.total_checks++
            if ($probe.ok) { $result.successful_checks++ } else { $result.failed_checks++ }
        }
        if ($round -lt $FileRounds -and $SleepSeconds -gt 0) {
            Start-Sleep -Seconds $SleepSeconds
        }
    }

    if ($result.total_checks -gt 0) {
        $result.success_rate_percent = [math]::Round((100.0 * $result.successful_checks / $result.total_checks), 2)
    }
    if ($result.successful_checks -eq $result.total_checks) {
        $result.classification = "STABLE"
    }
    elseif ($result.success_rate_percent -ge 90) {
        $result.classification = "MOSTLY_STABLE"
    }
    else {
        $result.classification = "BROKEN"
    }
    $result.stable_enough_for_chatgpt = ($result.classification -eq "STABLE" -or $result.classification -eq "MOSTLY_STABLE")
    $result["ended_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
    return $result
}

$sourceRoot = Resolve-SourceRoot
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
$runtime = Read-RuntimeState $runtimePath

$localUrl = if ($runtime.ContainsKey("local_url")) { [string]$runtime["local_url"] } else { "http://127.0.0.1:18080/" }
if ([string]::IsNullOrWhiteSpace($PublicUrl) -and $runtime.ContainsKey("public_url")) {
    $PublicUrl = [string]$runtime["public_url"]
}

$localRootCheck = Probe-Url $localUrl
$localStateCheck = Probe-Url ($localUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json")

$result = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $sourceRoot
    local_target_url = $localUrl
    public_url = $PublicUrl
    public_access_provider = "direct_local_pc_caddy"
    public_access_mechanism = "direct local-PC hosting via Caddy (non-tunnel canonical)"
    public_access_vpn_dependent = $false
    session_based_url = $false
    status = "FAIL"
    failure_cause = $null
    checks = [ordered]@{
        local_root_access = $localRootCheck
        local_public_state_access = $localStateCheck
    }
    stability_classification = $null
    stable_enough_for_chatgpt = $null
    repeated_checks_summary = $null
    stability_series = $null
}

if (-not $localRootCheck.ok -or -not $localStateCheck.ok) {
    $result.failure_cause = "canonical_local_caddy_web_not_reachable"
}
elseif ([string]::IsNullOrWhiteSpace($PublicUrl)) {
    $result.failure_cause = "router_port_forwarding_or_dns_mapping_not_configured"
}
else {
    $rootCheck = Probe-Url $PublicUrl
    $stateCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json")
    $syncCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/PUBLIC_SYNC_STATUS.json")
    $entryCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/PUBLIC_ENTRYPOINTS.md")
    $gitCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/.git/")
    $envCheck = Probe-Url ($PublicUrl.TrimEnd("/") + "/.env")
    $gitBlocked = ($gitCheck.ok -eq $false) -or ($gitCheck.status -ge 400)
    $envBlocked = ($envCheck.ok -eq $false) -or ($envCheck.status -ge 400)

    $result.checks["root_access"] = $rootCheck
    $result.checks["state_file_access"] = $stateCheck
    $result.checks["sync_status_file_access"] = $syncCheck
    $result.checks["entrypoints_file_access"] = $entryCheck
    $result.checks["git_path_blocked"] = [ordered]@{ pass = $gitBlocked; probe = $gitCheck }
    $result.checks["env_path_blocked"] = [ordered]@{ pass = $envBlocked; probe = $envCheck }

    if ($rootCheck.ok -and $stateCheck.ok -and $syncCheck.ok -and $entryCheck.ok -and $gitBlocked -and $envBlocked) {
        $result.status = "PASS"
    }
    else {
        $result.failure_cause = "router_port_forwarding_or_dns_mapping_not_configured"
    }
}

if ($RunStabilitySeries -and -not [string]::IsNullOrWhiteSpace($PublicUrl)) {
    $stability = Run-StabilitySeries -TargetUrl $PublicUrl -RootChecks $RootCheckCount -FileRounds $FileCheckRounds -SleepSeconds $IntervalSeconds
    $result.stability_series = $stability
    $result.stability_classification = $stability.classification
    $result.stable_enough_for_chatgpt = $stability.stable_enough_for_chatgpt
    $result.repeated_checks_summary = [ordered]@{
        passed = $stability.successful_checks
        total = $stability.total_checks
        failed = $stability.failed_checks
    }
    if ($stability.classification -eq "BROKEN") {
        $result.status = "FAIL"
        if ([string]::IsNullOrWhiteSpace($result.failure_cause)) {
            $result.failure_cause = "repeated_access_stability_broken"
        }
    }
}
elseif ($RunStabilitySeries) {
    $result.stability_series = [ordered]@{
        enabled = $true
        started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        root_checks_requested = $RootCheckCount
        file_rounds_requested = $FileCheckRounds
        interval_seconds = $IntervalSeconds
        root_checks = @()
        file_checks = [ordered]@{
            "/PUBLIC_REPO_STATE.json" = @()
            "/PUBLIC_SYNC_STATUS.json" = @()
            "/PUBLIC_ENTRYPOINTS.md" = @()
        }
        successful_checks = 0
        failed_checks = 0
        total_checks = 0
        success_rate_percent = 0
        classification = "BROKEN"
        stable_enough_for_chatgpt = $false
        session_based_url = $false
        ended_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        reason = "public_url_missing"
    }
    $result.stability_classification = "BROKEN"
    $result.stable_enough_for_chatgpt = $false
    $result.repeated_checks_summary = [ordered]@{
        passed = 0
        total = 0
        failed = 0
    }
}

$jsonPath = Join-Path $sourceRoot "setup_reports/public_access_check.json"
$mdPath = Join-Path $sourceRoot "setup_reports/public_access_check.md"
$result | ConvertTo-Json -Depth 14 | Set-Content -Path $jsonPath -Encoding UTF8

if ($RunStabilitySeries -and $result.stability_series -ne $null) {
    $stabilityJsonPath = Join-Path $sourceRoot "setup_reports/public_url_stability_check.json"
    $stabilityMdPath = Join-Path $sourceRoot "setup_reports/public_url_stability_check.md"
    $result.stability_series | ConvertTo-Json -Depth 14 | Set-Content -Path $stabilityJsonPath -Encoding UTF8

    $stabilityMd = @(
        "# Public URL Stability Check",
        "",
        "- checked_at_utc: $($result.checked_at_utc)",
        "- public_access_provider: $($result.public_access_provider)",
        "- public_access_mechanism: $($result.public_access_mechanism)",
        "- session_based_url: $($result.session_based_url)",
        "- final_public_url: $($result.public_url)",
        "- classification: $($result.stability_classification)",
        "- stable_enough_for_chatgpt: $($result.stable_enough_for_chatgpt)",
        "- repeated_checks_passed: $($result.repeated_checks_summary.passed)/$($result.repeated_checks_summary.total)",
        "- failed_checks: $($result.repeated_checks_summary.failed)"
    )
    $stabilityMd += ""
    $stabilityMd += "## Full Series JSON"
    $stabilityMd += '```json'
    $stabilityMd += ($result.stability_series | ConvertTo-Json -Depth 14)
    $stabilityMd += '```'
    Set-Content -Path $stabilityMdPath -Value $stabilityMd -Encoding UTF8
}

$md = @(
    "# Public Access Check",
    "",
    "- checked_at_utc: $($result.checked_at_utc)",
    "- local_target_url: $($result.local_target_url)",
    "- public_url: $($result.public_url)",
    "- public_access_provider: $($result.public_access_provider)",
    "- public_access_mechanism: $($result.public_access_mechanism)",
    "- public_access_vpn_dependent: $($result.public_access_vpn_dependent)",
    "- session_based_url: $($result.session_based_url)",
    "- stability_classification: $($result.stability_classification)",
    "- stable_enough_for_chatgpt: $($result.stable_enough_for_chatgpt)",
    "- repeated_checks_passed: $(if($result.repeated_checks_summary){$result.repeated_checks_summary.passed}else{'n/a'})/$(if($result.repeated_checks_summary){$result.repeated_checks_summary.total}else{'n/a'})",
    "- failure_cause: $($result.failure_cause)",
    "- status: $($result.status)",
    "",
    "## Checks"
)
foreach ($key in $result.checks.Keys) {
    $item = $result.checks[$key]
    $md += ""
    $md += "- $key"
    $md += '```json'
    $md += ($item | ConvertTo-Json -Depth 8)
    $md += '```'
}
Set-Content -Path $mdPath -Value $md -Encoding UTF8

$prevPassed = if ($result.repeated_checks_summary) { $result.repeated_checks_summary.passed } elseif ($runtime.ContainsKey("public_access_repeated_checks_passed")) { $runtime["public_access_repeated_checks_passed"] } else { $null }
$prevTotal = if ($result.repeated_checks_summary) { $result.repeated_checks_summary.total } elseif ($runtime.ContainsKey("public_access_repeated_checks_total")) { $runtime["public_access_repeated_checks_total"] } else { $null }
$prevClassification = if ($result.stability_classification) { $result.stability_classification } elseif ($runtime.ContainsKey("public_access_stability_classification")) { $runtime["public_access_stability_classification"] } else { $null }
$prevStable = if ($null -ne $result.stable_enough_for_chatgpt) { $result.stable_enough_for_chatgpt } elseif ($runtime.ContainsKey("public_access_stable_enough_for_chatgpt")) { $runtime["public_access_stable_enough_for_chatgpt"] } else { $null }

Write-RuntimePatch -PathValue $runtimePath -Patch ([ordered]@{
        public_access_provider = "direct_local_pc_caddy"
        public_access_mechanism = "direct local-PC hosting via Caddy (non-tunnel canonical)"
        public_access_vpn_dependent = $false
        public_access_session_based = $false
        public_access_stability_classification = $prevClassification
        public_access_stable_enough_for_chatgpt = $prevStable
        public_access_repeated_checks_passed = $prevPassed
        public_access_repeated_checks_total = $prevTotal
        router_port_forwarding_configured = ($result.status -eq "PASS")
        public_url_status = if ($result.status -eq "PASS") { "READY" } else { "NOT_READY" }
        public_url_blocker = if ($result.status -eq "PASS") { $null } else { $result.failure_cause }
        public_access_one_external_blocker = if ($result.status -eq "PASS") { $null } else { $result.failure_cause }
    })

Write-Host "[public-mirror-public] status=$($result.status) public_url=$PublicUrl"
Write-Host "[public-mirror-public] report_json=$jsonPath"
Write-Host "[public-mirror-public] report_md=$mdPath"

if ($result.status -ne "PASS") {
    exit 1
}
