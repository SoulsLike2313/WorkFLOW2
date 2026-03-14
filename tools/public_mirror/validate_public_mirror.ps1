param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [string]$PublicUrl
)

$ErrorActionPreference = "Stop"

function Get-RepoRoot {
    $root = (git rev-parse --show-toplevel).Trim()
    return (Resolve-Path $root).Path
}

function Get-RepoName {
    $remote = (git remote get-url origin 2>$null)
    if (-not [string]::IsNullOrWhiteSpace($remote)) {
        $leaf = Split-Path $remote -Leaf
        if ($leaf.EndsWith(".git")) {
            return [System.IO.Path]::GetFileNameWithoutExtension($leaf)
        }
        return $leaf
    }
    return [System.IO.Path]::GetFileName((Get-RepoRoot))
}

if ([string]::IsNullOrWhiteSpace($SourceRepoPath)) {
    $SourceRepoPath = Get-RepoRoot
}
else {
    $SourceRepoPath = (Resolve-Path $SourceRepoPath).Path
}
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $mirrorParent = Join-Path (Split-Path $SourceRepoPath -Parent) "_public_repo_mirror"
    $MirrorPath = Join-Path $mirrorParent (Get-RepoName)
}
$MirrorPath = [System.IO.Path]::GetFullPath($MirrorPath)

if ([string]::IsNullOrWhiteSpace($ExcludesFilePath)) {
    $ExcludesFilePath = Join-Path $SourceRepoPath "setup_reports/public_mirror_excludes.txt"
}
$ExcludesFilePath = [System.IO.Path]::GetFullPath($ExcludesFilePath)

$runtimeStatePath = Join-Path $SourceRepoPath "setup_reports/public_runtime_state.json"
if ([string]::IsNullOrWhiteSpace($PublicUrl) -and (Test-Path $runtimeStatePath)) {
    try {
        $runtime = Get-Content -Raw $runtimeStatePath | ConvertFrom-Json
        if (-not [string]::IsNullOrWhiteSpace($runtime.public_url)) {
            $PublicUrl = $runtime.public_url
        }
    }
    catch {}
}

$syncScript = Join-Path $SourceRepoPath "tools/public_mirror/sync_repo_to_public_mirror.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File $syncScript `
    -SourceRepoPath $SourceRepoPath `
    -MirrorPath $MirrorPath `
    -ExcludesFilePath $ExcludesFilePath `
    -PublicRuntimeStatePath $runtimeStatePath `
    -Quiet

$runId = "public-mirror-validate-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$results = [ordered]@{
    run_id = $runId
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $SourceRepoPath
    mirror_path = $MirrorPath
    public_url = $PublicUrl
    checks = [ordered]@{}
    status = "PASS"
}

function Set-Check($name, $pass, $details) {
    $results.checks[$name] = [ordered]@{
        pass = [bool]$pass
        details = $details
    }
    if (-not $pass -and $results.status -eq "PASS") {
        $results.status = "FAIL"
    }
}

$requiredMirrorFiles = @(
    "PUBLIC_REPO_STATE.json",
    "PUBLIC_REPO_STATE.md",
    "PUBLIC_SYNC_STATUS.json",
    "PUBLIC_SYNC_STATUS.md",
    "PUBLIC_ENTRYPOINTS.md"
)
$missing = @()
foreach ($rf in $requiredMirrorFiles) {
    if (-not (Test-Path (Join-Path $MirrorPath $rf))) {
        $missing += $rf
    }
}
Set-Check "required_public_state_files" ($missing.Count -eq 0) (@{ missing = $missing })

$probeRel = "setup_reports/.public_mirror_probe_$([guid]::NewGuid().ToString('N')).txt"
$probeSrc = Join-Path $SourceRepoPath $probeRel
$probeMirror = Join-Path $MirrorPath $probeRel
New-Item -ItemType Directory -Path (Split-Path $probeSrc -Parent) -Force | Out-Null
$probeContent = "probe-run=$runId"
Set-Content -Path $probeSrc -Value $probeContent -Encoding UTF8

& powershell -NoProfile -ExecutionPolicy Bypass -File $syncScript `
    -SourceRepoPath $SourceRepoPath `
    -MirrorPath $MirrorPath `
    -ExcludesFilePath $ExcludesFilePath `
    -PublicRuntimeStatePath $runtimeStatePath `
    -SkipFileManifest `
    -Quiet

$createPass = (Test-Path $probeMirror)
if ($createPass) {
    $mirrorContent = (Get-Content -Raw $probeMirror).Trim()
    $createPass = ($mirrorContent -eq $probeContent)
}
Set-Check "sync_create_propagation" $createPass (@{ source_probe = $probeSrc; mirror_probe = $probeMirror })

Remove-Item -Path $probeSrc -Force -ErrorAction SilentlyContinue
& powershell -NoProfile -ExecutionPolicy Bypass -File $syncScript `
    -SourceRepoPath $SourceRepoPath `
    -MirrorPath $MirrorPath `
    -ExcludesFilePath $ExcludesFilePath `
    -PublicRuntimeStatePath $runtimeStatePath `
    -SkipFileManifest `
    -Quiet

$deletePass = -not (Test-Path $probeMirror)
Set-Check "sync_delete_propagation" $deletePass (@{ mirror_probe_removed = $deletePass })

$sensitiveLocal = @(
    (Join-Path $MirrorPath ".git"),
    (Join-Path $MirrorPath ".env")
)
$sensitiveLeak = @()
foreach ($p in $sensitiveLocal) {
    if (Test-Path $p) {
        $sensitiveLeak += $p
    }
}
Set-Check "sensitive_local_path_block" ($sensitiveLeak.Count -eq 0) (@{ leaked_paths = $sensitiveLeak })

if (-not [string]::IsNullOrWhiteSpace($PublicUrl)) {
    $publicChecks = [ordered]@{
        root_list_ok = $false
        state_file_ok = $false
        sensitive_git_blocked = $false
        sensitive_env_blocked = $false
    }
    try {
        $root = Invoke-WebRequest -Uri $PublicUrl -UseBasicParsing -TimeoutSec 20
        $publicChecks.root_list_ok = ($root.StatusCode -ge 200 -and $root.StatusCode -lt 400)
    }
    catch {}
    try {
        $stateResp = Invoke-WebRequest -Uri ($PublicUrl.TrimEnd("/") + "/PUBLIC_REPO_STATE.json") -UseBasicParsing -TimeoutSec 20
        $publicChecks.state_file_ok = ($stateResp.StatusCode -ge 200 -and $stateResp.StatusCode -lt 400)
    }
    catch {}
    try {
        $gitResp = Invoke-WebRequest -Uri ($PublicUrl.TrimEnd("/") + "/.git/") -UseBasicParsing -TimeoutSec 20
        $publicChecks.sensitive_git_blocked = ($gitResp.StatusCode -ge 400)
    }
    catch {
        $publicChecks.sensitive_git_blocked = $true
    }
    try {
        $envResp = Invoke-WebRequest -Uri ($PublicUrl.TrimEnd("/") + "/.env") -UseBasicParsing -TimeoutSec 20
        $publicChecks.sensitive_env_blocked = ($envResp.StatusCode -ge 400)
    }
    catch {
        $publicChecks.sensitive_env_blocked = $true
    }

    $publicPass = $publicChecks.root_list_ok -and $publicChecks.state_file_ok -and $publicChecks.sensitive_git_blocked -and $publicChecks.sensitive_env_blocked
    Set-Check "public_url_access_and_safety" $publicPass $publicChecks
}
else {
    Set-Check "public_url_access_and_safety" $false (@{ reason = "public_url_not_available" })
}

$jsonPath = Join-Path $SourceRepoPath "setup_reports/public_repo_access_validation.json"
$mdPath = Join-Path $SourceRepoPath "setup_reports/public_repo_access_validation.md"
$results | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Repo Access Validation",
    "",
    "- run_id: $runId",
    "- generated_at_utc: $($results.generated_at_utc)",
    "- source_repo_path: $SourceRepoPath",
    "- mirror_path: $MirrorPath",
    "- public_url: $PublicUrl",
    "- status: $($results.status)",
    "",
    "## Checks"
)
foreach ($k in $results.checks.Keys) {
    $item = $results.checks[$k]
    $md += ""
    $md += "- $k: $($item.pass)"
    $md += "```json"
    $md += ($item.details | ConvertTo-Json -Depth 6)
    $md += "```"
}
Set-Content -Path $mdPath -Value $md -Encoding UTF8

Write-Host "[public-mirror] validation run: $runId"
Write-Host "[public-mirror] status: $($results.status)"
Write-Host "[public-mirror] report_json: $jsonPath"
Write-Host "[public-mirror] report_md: $mdPath"

if ($results.status -ne "PASS") {
    exit 1
}
