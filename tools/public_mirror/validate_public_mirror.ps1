param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [string]$PublicUrl
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

function Set-Check([hashtable]$Results, [string]$Name, [bool]$Pass, $Details) {
    $Results.checks[$Name] = [ordered]@{
        pass = $Pass
        details = $Details
    }
    if (-not $Pass -and $Results.status -eq "PASS") {
        $Results.status = "FAIL"
    }
}

function Run-ScriptCapture([string]$ScriptPath, [string[]]$Args) {
    $allArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $ScriptPath) + $Args
    $text = & powershell @allArgs 2>&1
    $exitCode = $LASTEXITCODE
    return [ordered]@{
        exit_code = $exitCode
        output = @($text | ForEach-Object { "$_" })
    }
}

$sourceRoot = Resolve-SourceRoot
$repoName = Resolve-RepoName $sourceRoot
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}
if ([string]::IsNullOrWhiteSpace($ExcludesFilePath)) {
    $ExcludesFilePath = Join-Path $sourceRoot "setup_reports/public_mirror_excludes.txt"
}

$sourceRoot = [System.IO.Path]::GetFullPath($sourceRoot)
$mirrorRoot = [System.IO.Path]::GetFullPath($MirrorPath)
$excludesPath = [System.IO.Path]::GetFullPath($ExcludesFilePath)
$runtimePath = Join-Path $sourceRoot "setup_reports/public_runtime_state.json"
if ([string]::IsNullOrWhiteSpace($PublicUrl) -and (Test-Path $runtimePath)) {
    try {
        $runtime = Get-Content -Raw $runtimePath | ConvertFrom-Json
        if (-not [string]::IsNullOrWhiteSpace($runtime.public_url)) {
            $PublicUrl = $runtime.public_url
        }
    }
    catch {}
}

$runId = "public-mirror-validate-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$results = [ordered]@{
    run_id = $runId
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    source_repo_path = $sourceRoot
    mirror_path = $mirrorRoot
    public_url = $PublicUrl
    checks = [ordered]@{}
    status = "PASS"
}

$fastScript = Join-Path $sourceRoot "tools/public_mirror/fast_resume_public_mirror.ps1"
$syncRun = Run-ScriptCapture -ScriptPath $fastScript -Args @(
    "-SourceRepoPath", $sourceRoot,
    "-MirrorPath", $mirrorRoot,
    "-ExcludesFilePath", $excludesPath,
    "-StageATimeBudgetSeconds", "120",
    "-StageBTimeBudgetSeconds", "180"
)
Set-Check -Results $results -Name "fast_resume_sync" -Pass ($syncRun.exit_code -eq 0) -Details $syncRun

$requiredMirrorFiles = @(
    "PUBLIC_REPO_STATE.json",
    "PUBLIC_REPO_STATE.md",
    "PUBLIC_SYNC_STATUS.json",
    "PUBLIC_SYNC_STATUS.md",
    "PUBLIC_ENTRYPOINTS.md"
)
$missing = @()
foreach ($rf in $requiredMirrorFiles) {
    if (-not (Test-Path (Join-Path $mirrorRoot $rf))) {
        $missing += $rf
    }
}
Set-Check -Results $results -Name "required_public_state_files" -Pass ($missing.Count -eq 0) -Details (@{ missing = $missing })

$probeRel = "setup_reports/.public_mirror_probe_$([guid]::NewGuid().ToString('N')).txt"
$probeSrc = Join-Path $sourceRoot $probeRel
$probeMirror = Join-Path $mirrorRoot $probeRel
New-Item -ItemType Directory -Path (Split-Path $probeSrc -Parent) -Force | Out-Null
$probeContent = "probe-run=$runId"
Set-Content -Path $probeSrc -Value $probeContent -Encoding UTF8

$syncCreate = Run-ScriptCapture -ScriptPath $fastScript -Args @(
    "-SourceRepoPath", $sourceRoot,
    "-MirrorPath", $mirrorRoot,
    "-ExcludesFilePath", $excludesPath,
    "-StageATimeBudgetSeconds", "90",
    "-StageBTimeBudgetSeconds", "90"
)
$createPass = ($syncCreate.exit_code -eq 0) -and (Test-Path $probeMirror)
if ($createPass) {
    $mirrorContent = (Get-Content -Raw $probeMirror).Trim()
    $createPass = ($mirrorContent -eq $probeContent)
}
Set-Check -Results $results -Name "sync_create_propagation" -Pass $createPass -Details (@{
        source_probe = $probeSrc
        mirror_probe = $probeMirror
        sync = $syncCreate
    })

Remove-Item -Path $probeSrc -Force -ErrorAction SilentlyContinue
$syncDelete = Run-ScriptCapture -ScriptPath $fastScript -Args @(
    "-SourceRepoPath", $sourceRoot,
    "-MirrorPath", $mirrorRoot,
    "-ExcludesFilePath", $excludesPath,
    "-StageATimeBudgetSeconds", "90",
    "-StageBTimeBudgetSeconds", "90"
)
$deletePass = ($syncDelete.exit_code -eq 0) -and (-not (Test-Path $probeMirror))
Set-Check -Results $results -Name "sync_delete_propagation" -Pass $deletePass -Details (@{
        mirror_probe_removed = $deletePass
        sync = $syncDelete
    })

$sensitivePatterns = @(".git", ".env", "*.pem", "*.key", "*.p12", "*.pfx")
$leaks = @()
foreach ($pat in $sensitivePatterns) {
    $found = Get-ChildItem -Path $mirrorRoot -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -like $pat }
    if ($found) {
        $leaks += @($found | Select-Object -ExpandProperty FullName)
    }
}
$leaks = @($leaks | Sort-Object -Unique)
Set-Check -Results $results -Name "sensitive_paths_not_present" -Pass ($leaks.Count -eq 0) -Details (@{ leaked_paths = $leaks })

$webCheckScript = Join-Path $sourceRoot "tools/public_mirror/check_public_mirror_web.ps1"
$webCheck = Run-ScriptCapture -ScriptPath $webCheckScript -Args @(
    "-SourceRepoPath", $sourceRoot,
    "-MirrorPath", $mirrorRoot
)
Set-Check -Results $results -Name "local_web_access_and_safety" -Pass ($webCheck.exit_code -eq 0) -Details $webCheck

if (-not [string]::IsNullOrWhiteSpace($PublicUrl)) {
    $publicCheckScript = Join-Path $sourceRoot "tools/public_mirror/check_public_mirror_public_access.ps1"
    $publicCheck = Run-ScriptCapture -ScriptPath $publicCheckScript -Args @(
        "-SourceRepoPath", $sourceRoot,
        "-PublicUrl", $PublicUrl
    )
    Set-Check -Results $results -Name "public_url_access_and_safety" -Pass ($publicCheck.exit_code -eq 0) -Details $publicCheck
}
else {
    Set-Check -Results $results -Name "public_url_access_and_safety" -Pass $false -Details (@{ reason = "public_url_not_available" })
}

$jsonPath = Join-Path $sourceRoot "setup_reports/public_repo_access_validation.json"
$mdPath = Join-Path $sourceRoot "setup_reports/public_repo_access_validation.md"
$results | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonPath -Encoding UTF8

$md = @(
    "# Public Repo Access Validation",
    "",
    "- run_id: $runId",
    "- generated_at_utc: $($results.generated_at_utc)",
    "- source_repo_path: $sourceRoot",
    "- mirror_path: $mirrorRoot",
    "- public_url: $PublicUrl",
    "- status: $($results.status)",
    "",
    "## Checks"
)
foreach ($k in $results.checks.Keys) {
    $item = $results.checks[$k]
    $md += ""
    $md += ("- {0}: {1}" -f $k, $item.pass)
    $md += '```json'
    $md += ($item.details | ConvertTo-Json -Depth 8)
    $md += '```'
}
Set-Content -Path $mdPath -Value $md -Encoding UTF8

Write-Host "[public-mirror] validation run: $runId"
Write-Host "[public-mirror] status: $($results.status)"
Write-Host "[public-mirror] report_json: $jsonPath"
Write-Host "[public-mirror] report_md: $mdPath"

if ($results.status -ne "PASS") {
    exit 1
}
