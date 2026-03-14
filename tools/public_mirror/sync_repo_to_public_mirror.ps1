param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [string]$PublicRuntimeStatePath,
    [switch]$SkipFileManifest,
    [switch]$Quiet
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

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Get-ExcludeRules([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        throw "Exclude rules file not found: $PathValue"
    }
    return @(Get-Content $PathValue | Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and -not $_.TrimStart().StartsWith("#") })
}

function Classify-ExcludeRules([string[]]$Rules, [string]$SourceRoot) {
    $excludeDirs = New-Object System.Collections.Generic.List[string]
    $excludeFiles = New-Object System.Collections.Generic.List[string]

    foreach ($rule in $Rules) {
        $trim = $rule.Trim()
        if ([string]::IsNullOrWhiteSpace($trim)) {
            continue
        }

        $isWildcard = ($trim.Contains("*") -or $trim.Contains("?"))
        $normalized = $trim.Replace("/", "\")

        if ($isWildcard) {
            $excludeFiles.Add($trim)
            continue
        }

        $candidate = Join-Path $SourceRoot ($normalized.TrimEnd("\"))
        if ($trim.EndsWith("/") -or (Test-Path $candidate -PathType Container)) {
            $excludeDirs.Add($candidate)
            continue
        }

        if (Test-Path $candidate -PathType Leaf) {
            $excludeFiles.Add($candidate)
            continue
        }

        if ($normalized -notmatch "[\\]") {
            $excludeFiles.Add($trim)
        }
        else {
            $excludeFiles.Add($candidate)
        }
    }

    return @{
        exclude_dirs = @($excludeDirs | Sort-Object -Unique)
        exclude_files = @($excludeFiles | Sort-Object -Unique)
    }
}

function Write-MarkdownFile([string]$PathValue, [string[]]$Lines) {
    Set-Content -Path $PathValue -Value $Lines -Encoding UTF8
}

if ([string]::IsNullOrWhiteSpace($SourceRepoPath)) {
    $SourceRepoPath = Get-RepoRoot
}
else {
    $SourceRepoPath = (Resolve-Path $SourceRepoPath).Path
}

$repoName = Get-RepoName
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $mirrorParent = Join-Path (Split-Path $SourceRepoPath -Parent) "_public_repo_mirror"
    $MirrorPath = Join-Path $mirrorParent $repoName
}

if ([string]::IsNullOrWhiteSpace($ExcludesFilePath)) {
    $ExcludesFilePath = Join-Path $SourceRepoPath "setup_reports/public_mirror_excludes.txt"
}

if ([string]::IsNullOrWhiteSpace($PublicRuntimeStatePath)) {
    $PublicRuntimeStatePath = Join-Path $SourceRepoPath "setup_reports/public_runtime_state.json"
}

$MirrorPath = [System.IO.Path]::GetFullPath($MirrorPath)
$ExcludesFilePath = [System.IO.Path]::GetFullPath($ExcludesFilePath)
$PublicRuntimeStatePath = [System.IO.Path]::GetFullPath($PublicRuntimeStatePath)

Ensure-Directory (Split-Path $MirrorPath -Parent)
Ensure-Directory $MirrorPath
Ensure-Directory (Join-Path $SourceRepoPath "setup_reports")

$runId = "public-sync-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$rules = Get-ExcludeRules -PathValue $ExcludesFilePath
$classified = Classify-ExcludeRules -Rules $rules -SourceRoot $SourceRepoPath

$robocopyArgs = @(
    $SourceRepoPath,
    $MirrorPath,
    "/MIR",
    "/R:1",
    "/W:1",
    "/XJ",
    "/FFT",
    "/NP",
    "/NDL",
    "/NFL",
    "/NJH",
    "/NJS"
)

if ($classified.exclude_dirs.Count -gt 0) {
    $robocopyArgs += "/XD"
    $robocopyArgs += $classified.exclude_dirs
}
if ($classified.exclude_files.Count -gt 0) {
    $robocopyArgs += "/XF"
    $robocopyArgs += $classified.exclude_files
}

if (-not $Quiet) {
    Write-Host "[public-mirror] robocopy start: $runId"
}

& robocopy @robocopyArgs | Out-Null
$robocopyExitCode = $LASTEXITCODE
if ($robocopyExitCode -ge 8) {
    throw "robocopy failed with exit code $robocopyExitCode"
}

Push-Location $SourceRepoPath
$sourceBranch = (git rev-parse --abbrev-ref HEAD).Trim()
$sourceHead = (git rev-parse HEAD).Trim()
$gitStatus = @(git status --porcelain)
Pop-Location

$runtimeState = $null
if (Test-Path $PublicRuntimeStatePath) {
    try {
        $runtimeState = Get-Content -Raw $PublicRuntimeStatePath | ConvertFrom-Json
    }
    catch {
        $runtimeState = $null
    }
}

$publicUrl = $null
$localUrl = "http://127.0.0.1:18080/"
if ($runtimeState -ne $null) {
    if (-not [string]::IsNullOrWhiteSpace($runtimeState.public_url)) {
        $publicUrl = $runtimeState.public_url
    }
    if (-not [string]::IsNullOrWhiteSpace($runtimeState.local_url)) {
        $localUrl = $runtimeState.local_url
    }
}

$mirrorFiles = Get-ChildItem -Path $MirrorPath -Recurse -File -Force -ErrorAction SilentlyContinue
$totalMirroredFiles = ($mirrorFiles | Measure-Object).Count
$syncTime = (Get-Date).ToUniversalTime().ToString("o")

$manifestPath = Join-Path $MirrorPath "PUBLIC_FILE_MANIFEST.json"
if (-not $SkipFileManifest) {
    $manifest = [ordered]@{
        generated_at_utc = $syncTime
        mirror_path = $MirrorPath
        total_files = $totalMirroredFiles
        files = @(
            $mirrorFiles | ForEach-Object {
                [ordered]@{
                    path = ($_.FullName.Substring($MirrorPath.Length) -replace "^[\\/]+", "" -replace "\\", "/")
                    size_bytes = $_.Length
                    last_write_utc = $_.LastWriteTimeUtc.ToString("o")
                }
            }
        )
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding UTF8
}

$stateJsonPath = Join-Path $MirrorPath "PUBLIC_REPO_STATE.json"
$stateMdPath = Join-Path $MirrorPath "PUBLIC_REPO_STATE.md"
$statusJsonPath = Join-Path $MirrorPath "PUBLIC_SYNC_STATUS.json"
$statusMdPath = Join-Path $MirrorPath "PUBLIC_SYNC_STATUS.md"
$entrypointsMdPath = Join-Path $MirrorPath "PUBLIC_ENTRYPOINTS.md"

$state = [ordered]@{
    github_is_not_source_of_truth = $true
    source_repo_path = $SourceRepoPath
    mirror_path = $MirrorPath
    public_url = $publicUrl
    local_url = $localUrl
    timestamp_last_sync_utc = $syncTime
    source_branch = $sourceBranch
    source_head_commit = $sourceHead
    git_status_summary = [ordered]@{
        clean = ($gitStatus.Count -eq 0)
        changed_count = $gitStatus.Count
        porcelain = @($gitStatus)
    }
    total_mirrored_files = $totalMirroredFiles
    exclude_rules_used = @($rules)
    known_limitations = @(
        "Mirror excludes sensitive files/paths from setup_reports/public_mirror_excludes.txt",
        "Public URL may be tunnel-based and can rotate after restart"
    )
    recommended_entry_files = @(
        "README.md",
        "docs/CURRENT_PLATFORM_STATE.md",
        "docs/NEXT_CANONICAL_STEP.md",
        "workspace_config/workspace_manifest.json",
        "workspace_config/codex_manifest.json",
        "workspace_config/TASK_RULES.md",
        "workspace_config/AGENT_EXECUTION_POLICY.md",
        "workspace_config/MACHINE_REPO_READING_RULES.md"
    )
    active_project_path = "projects/platform_test_agent"
    next_canonical_step_path = "docs/NEXT_CANONICAL_STEP.md"
    file_manifest_path = if (Test-Path $manifestPath) { "PUBLIC_FILE_MANIFEST.json" } else { $null }
}
$state | ConvertTo-Json -Depth 8 | Set-Content -Path $stateJsonPath -Encoding UTF8

$stateMd = @(
    "# Public Repo State",
    "",
    "- github_is_not_source_of_truth: true",
    "- source_repo_path: $SourceRepoPath",
    "- mirror_path: $MirrorPath",
    "- public_url: $publicUrl",
    "- local_url: $localUrl",
    "- timestamp_last_sync_utc: $syncTime",
    "- source_branch: $sourceBranch",
    "- source_head_commit: $sourceHead",
    "- total_mirrored_files: $totalMirroredFiles",
    "",
    "## git status summary",
    "",
    '```text'
)
if ($gitStatus.Count -eq 0) {
    $stateMd += "(clean)"
}
else {
    $stateMd += $gitStatus
}
$stateMd += '```'
$stateMd += ""
$stateMd += "## exclude rules used"
$stateMd += ""
$stateMd += '```text'
$stateMd += $rules
$stateMd += '```'
Write-MarkdownFile -PathValue $stateMdPath -Lines $stateMd

$status = [ordered]@{
    run_id = $runId
    status = "PASS"
    sync_time_utc = $syncTime
    source_repo_path = $SourceRepoPath
    mirror_path = $MirrorPath
    robocopy_exit_code = $robocopyExitCode
    total_mirrored_files = $totalMirroredFiles
    skip_file_manifest = [bool]$SkipFileManifest
}
$status | ConvertTo-Json -Depth 5 | Set-Content -Path $statusJsonPath -Encoding UTF8

$statusMd = @(
    "# Public Sync Status",
    "",
    "- run_id: $runId",
    "- status: PASS",
    "- sync_time_utc: $syncTime",
    "- source_repo_path: $SourceRepoPath",
    "- mirror_path: $MirrorPath",
    "- robocopy_exit_code: $robocopyExitCode",
    "- total_mirrored_files: $totalMirroredFiles",
    "- skip_file_manifest: $([bool]$SkipFileManifest)"
)
Write-MarkdownFile -PathValue $statusMdPath -Lines $statusMd

$entrypointsMd = @(
    "# Public Entrypoints",
    "",
    "## Recommended Start Files",
    "",
    "1. README.md",
    "2. docs/CURRENT_PLATFORM_STATE.md",
    "3. docs/NEXT_CANONICAL_STEP.md",
    "4. workspace_config/workspace_manifest.json",
    "5. workspace_config/codex_manifest.json",
    "6. workspace_config/TASK_RULES.md",
    "7. workspace_config/AGENT_EXECUTION_POLICY.md",
    "8. workspace_config/MACHINE_REPO_READING_RULES.md",
    "",
    "## Governance Core",
    "",
    "- workspace_config/EXECUTION_ADMISSION_POLICY.md",
    "- workspace_config/TASK_SOURCE_POLICY.md",
    "- workspace_config/COMMUNICATION_STYLE_POLICY.md",
    "- workspace_config/GITHUB_SYNC_POLICY.md",
    "- workspace_config/COMPLETION_GATE_RULES.md",
    "",
    "## Active Project",
    "",
    "- projects/platform_test_agent"
)
Write-MarkdownFile -PathValue $entrypointsMdPath -Lines $entrypointsMd

$localSummary = [ordered]@{
    run_id = $runId
    sync_time_utc = $syncTime
    source_repo_path = $SourceRepoPath
    mirror_path = $MirrorPath
    source_branch = $sourceBranch
    source_head_commit = $sourceHead
    robocopy_exit_code = $robocopyExitCode
    total_mirrored_files = $totalMirroredFiles
    public_url = $publicUrl
}
$localSummaryPath = Join-Path $SourceRepoPath "setup_reports/public_sync_last_run.json"
$localSummary | ConvertTo-Json -Depth 5 | Set-Content -Path $localSummaryPath -Encoding UTF8

if (-not $Quiet) {
    Write-Host "[public-mirror] sync complete: $runId"
    Write-Host "[public-mirror] mirror_path: $MirrorPath"
    Write-Host "[public-mirror] total_files: $totalMirroredFiles"
}
