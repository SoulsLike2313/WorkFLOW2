param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$LocalUrl
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

function Try-Get([string]$Url) {
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
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
$repoName = Resolve-RepoName $sourceRoot
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}

$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
$runtime = Read-RuntimeState $runtimePath
if ([string]::IsNullOrWhiteSpace($LocalUrl) -and $runtime.ContainsKey("local_url")) {
    $LocalUrl = [string]$runtime["local_url"]
}
if ([string]::IsNullOrWhiteSpace($LocalUrl)) {
    $LocalUrl = "http://127.0.0.1:18080/"
}

$rootCheck = Try-Get $LocalUrl
$stateCheck = Try-Get ($LocalUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json")
$gitCheck = Try-Get ($LocalUrl.TrimEnd("/") + "/.git/")
$envCheck = Try-Get ($LocalUrl.TrimEnd("/") + "/.env")

$gitBlocked = ($gitCheck.ok -eq $false) -or ($gitCheck.status -ge 400)
$envBlocked = ($envCheck.ok -eq $false) -or ($envCheck.status -ge 400)

$result = [ordered]@{
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $sourceRoot
    mirror_path = [System.IO.Path]::GetFullPath($MirrorPath)
    local_url = $LocalUrl
    checks = [ordered]@{
        root_access = $rootCheck
        public_repo_state_access = $stateCheck
        git_path_blocked = [ordered]@{ pass = $gitBlocked; probe = $gitCheck }
        env_path_blocked = [ordered]@{ pass = $envBlocked; probe = $envCheck }
    }
}

$pass = $rootCheck.ok -and $stateCheck.ok -and $gitBlocked -and $envBlocked
$result["status"] = if ($pass) { "PASS" } else { "FAIL" }

$jsonPath = Join-Path $sourceRoot "setup_reports/public_mirror_web_check.json"
$mdPath = Join-Path $sourceRoot "setup_reports/public_mirror_web_check.md"
$result | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Mirror Web Check",
    "",
    "- checked_at_utc: $($result.checked_at_utc)",
    "- local_url: $LocalUrl",
    "- status: $($result.status)",
    "",
    "## Checks",
    "",
    "- root_access: $($rootCheck.ok) status=$($rootCheck.status)",
    "- public_repo_state_access: $($stateCheck.ok) status=$($stateCheck.status)",
    "- git_path_blocked: $gitBlocked",
    "- env_path_blocked: $envBlocked"
)
Set-Content -Path $mdPath -Value $md -Encoding UTF8

Write-Host "[public-mirror-web] status=$($result.status) local_url=$LocalUrl"
Write-Host "[public-mirror-web] report_json=$jsonPath"
Write-Host "[public-mirror-web] report_md=$mdPath"

if (-not $pass) {
    exit 1
}
