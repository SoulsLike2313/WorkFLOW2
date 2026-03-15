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
        try { return (Get-Content -Raw $PathValue | ConvertFrom-Json -AsHashtable) } catch {}
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
    status = "FAIL"
    checks = [ordered]@{}
}

if ([string]::IsNullOrWhiteSpace($PublicUrl)) {
    $result.checks["public_url_present"] = [ordered]@{
        pass = $false
        reason = "public_url_missing"
    }
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
}

$jsonPath = Join-Path $sourceRoot "setup_reports/public_access_check.json"
$mdPath = Join-Path $sourceRoot "setup_reports/public_access_check.md"
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Access Check",
    "",
    "- checked_at_utc: $($result.checked_at_utc)",
    "- public_url: $($result.public_url)",
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
