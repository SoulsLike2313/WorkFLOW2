param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [int]$StageATimeBudgetSeconds = 300,
    [int]$StageBTimeBudgetSeconds = 600,
    [int]$StageCTimeBudgetSeconds = 600,
    [switch]$RunHeavyTail
)

$ErrorActionPreference = "Stop"

function Resolve-SourceRepo {
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

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Load-Excludes([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        throw "Excludes file not found: $PathValue"
    }
    return @(Get-Content $PathValue | Where-Object { -not [string]::IsNullOrWhiteSpace($_) -and -not $_.TrimStart().StartsWith("#") })
}

function Classify-ExcludeRules([string[]]$Rules, [string]$SourceRoot) {
    $dirs = New-Object System.Collections.Generic.List[string]
    $files = New-Object System.Collections.Generic.List[string]
    foreach ($rule in $Rules) {
        $trim = $rule.Trim()
        if ([string]::IsNullOrWhiteSpace($trim)) { continue }
        $isWildcard = ($trim.Contains("*") -or $trim.Contains("?"))
        $normalized = $trim.Replace("/", "\")
        if ($isWildcard) {
            $files.Add($trim)
            continue
        }
        $candidate = Join-Path $SourceRoot ($normalized.TrimEnd("\"))
        if ($trim.EndsWith("/") -or (Test-Path $candidate -PathType Container)) {
            $dirs.Add($candidate)
        }
        elseif (Test-Path $candidate -PathType Leaf) {
            $files.Add($candidate)
        }
        elseif ($normalized -notmatch "[\\]") {
            $files.Add($trim)
        }
        else {
            $files.Add($candidate)
        }
    }
    return @{
        exclude_dirs = @($dirs | Sort-Object -Unique)
        exclude_files = @($files | Sort-Object -Unique)
    }
}

function Convert-ToArgumentString([string[]]$ArgumentItems) {
    return ($ArgumentItems | ForEach-Object {
            if ($_ -match '\s') { '"' + $_.Replace('"', '\"') + '"' } else { $_ }
        }) -join ' '
}

function Invoke-RoboCopyStage {
    param(
        [string]$Label,
        [string]$Src,
        [string]$Dst,
        [string[]]$BaseExcludeDirs,
        [string[]]$BaseExcludeFiles,
        [string[]]$ExtraExcludeDirs,
        [string[]]$ExtraExcludeFiles,
        [int]$TimeBudgetSeconds,
        [string]$LogPath
    )

    Ensure-Directory $Dst
    Ensure-Directory (Split-Path $LogPath -Parent)

    $allExcludeDirs = @($BaseExcludeDirs + $ExtraExcludeDirs | Sort-Object -Unique)
    $allExcludeFiles = @($BaseExcludeFiles + $ExtraExcludeFiles | Sort-Object -Unique)

    $args = @(
        $Src,
        $Dst,
        "/MIR",
        "/MT:32",
        "/R:1",
        "/W:1",
        "/FFT",
        "/XJ",
        "/NP",
        "/NFL",
        "/NDL",
        "/NJH",
        "/NJS"
    )
    if ($allExcludeDirs.Count -gt 0) {
        $args += "/XD"
        $args += $allExcludeDirs
    }
    if ($allExcludeFiles.Count -gt 0) {
        $args += "/XF"
        $args += $allExcludeFiles
    }

    $argumentString = Convert-ToArgumentString $args
    $proc = Start-Process -FilePath "robocopy" -ArgumentList $argumentString -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $LogPath -RedirectStandardError ($LogPath + ".err")

    $timedOut = $false
    try {
        Wait-Process -Id $proc.Id -Timeout $TimeBudgetSeconds -ErrorAction Stop
    }
    catch {
        $timedOut = $true
        try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
    }

    $exitCode = $null
    if (-not $timedOut) {
        $exitCode = $proc.ExitCode
    }

    $pass = (-not $timedOut) -and ($exitCode -lt 8)
    $status = if ($pass) { "PASS" } elseif ($timedOut) { "TIME_BUDGET_REACHED" } else { "FAIL" }

    return [ordered]@{
        label = $Label
        source = $Src
        destination = $Dst
        time_budget_seconds = $TimeBudgetSeconds
        timed_out = $timedOut
        robocopy_exit_code = $exitCode
        status = $status
        log_path = $LogPath
        error_log_path = ($LogPath + ".err")
        finished_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
}

function Get-MirrorStats([string]$MirrorRoot) {
    if (-not (Test-Path $MirrorRoot)) {
        return @{
            files = 0
            directories = 0
            size_bytes = 0
        }
    }
    $files = Get-ChildItem -Path $MirrorRoot -Recurse -File -Force -ErrorAction SilentlyContinue
    $dirs = Get-ChildItem -Path $MirrorRoot -Recurse -Directory -Force -ErrorAction SilentlyContinue
    return @{
        files = ($files | Measure-Object).Count
        directories = ($dirs | Measure-Object).Count
        size_bytes = [int64](($files | Measure-Object Length -Sum).Sum)
    }
}

function Write-ProgressStatus {
    param(
        [hashtable]$ProgressObject,
        [string]$JsonPath,
        [string]$MdPath
    )
    $ProgressObject | ConvertTo-Json -Depth 10 | Set-Content -Path $JsonPath -Encoding UTF8
    $md = @(
        "# Public Mirror Progress Status",
        "",
        "- updated_at_utc: $($ProgressObject.updated_at_utc)",
        "- mode: $($ProgressObject.mode)",
        "- source_path: $($ProgressObject.source_path)",
        "- mirror_path: $($ProgressObject.mirror_path)",
        "- engineering_ready: $($ProgressObject.engineering_ready)",
        "- current_stage: $($ProgressObject.current_stage)",
        "- status: $($ProgressObject.status)",
        "",
        "## Stage Results"
    )
    foreach ($stage in $ProgressObject.stage_results) {
        $md += ""
        $md += "- stage=$($stage.label) status=$($stage.status) timeout=$($stage.timed_out) exit_code=$($stage.robocopy_exit_code)"
        $md += "  log: $($stage.log_path)"
    }
    $md += ""
    $md += "## Mirror Stats"
    $md += ""
    $md += "- files: $($ProgressObject.mirror_stats.files)"
    $md += "- directories: $($ProgressObject.mirror_stats.directories)"
    $md += "- size_bytes: $($ProgressObject.mirror_stats.size_bytes)"
    Set-Content -Path $MdPath -Value $md -Encoding UTF8
}

function Write-PublicStateFiles {
    param(
        [string]$SourceRoot,
        [string]$MirrorRoot,
        [string[]]$Excludes,
        [string]$Stage,
        [bool]$EngineeringReady,
        [string]$Status,
        [hashtable]$MirrorStats
    )

    $branch = (git -C $SourceRoot rev-parse --abbrev-ref HEAD).Trim()
    $head = (git -C $SourceRoot rev-parse HEAD).Trim()
    $gitStatus = @(git -C $SourceRoot status --porcelain)
    $syncTime = (Get-Date).ToUniversalTime().ToString("o")
    $publicUrl = $null
    $runtimeStatePath = Join-Path $SourceRoot "setup_reports/public_runtime_state.json"
    if (Test-Path $runtimeStatePath) {
        try {
            $runtimeState = Get-Content -Raw $runtimeStatePath | ConvertFrom-Json
            if (-not [string]::IsNullOrWhiteSpace($runtimeState.public_url)) {
                $publicUrl = $runtimeState.public_url
            }
        }
        catch {}
    }

    $state = [ordered]@{
        github_is_not_source_of_truth = $true
        source_repo_path = $SourceRoot
        mirror_path = $MirrorRoot
        public_url = $publicUrl
        timestamp_last_sync_utc = $syncTime
        source_branch = $branch
        source_head_commit = $head
        git_status_summary = [ordered]@{
            clean = ($gitStatus.Count -eq 0)
            changed_count = $gitStatus.Count
        }
        current_stage = $Stage
        engineering_ready = $EngineeringReady
        sync_status = $Status
        total_mirrored_files = $MirrorStats.files
        total_mirrored_directories = $MirrorStats.directories
        total_mirror_size_bytes = $MirrorStats.size_bytes
        exclude_rules_used = $Excludes
        known_limitations = @(
            "Heavy tail directories can be synced later via fast resume stage C",
            "Full file manifest is not regenerated on every fast pass"
        )
        recommended_entry_files = @(
            "README.md",
            "docs/CURRENT_PLATFORM_STATE.md",
            "docs/NEXT_CANONICAL_STEP.md",
            "workspace_config/workspace_manifest.json",
            "workspace_config/codex_manifest.json",
            "workspace_config/TASK_RULES.md"
        )
    }
    $state | ConvertTo-Json -Depth 8 | Set-Content -Path (Join-Path $MirrorRoot "PUBLIC_REPO_STATE.json") -Encoding UTF8

    $stateMd = @(
        "# Public Repo State",
        "",
        "- source_repo_path: $SourceRoot",
        "- mirror_path: $MirrorRoot",
        "- source_branch: $branch",
        "- source_head_commit: $head",
        "- current_stage: $Stage",
        "- engineering_ready: $EngineeringReady",
        "- sync_status: $Status",
        "- total_mirrored_files: $($MirrorStats.files)",
        "- total_mirrored_directories: $($MirrorStats.directories)",
        "- total_mirror_size_bytes: $($MirrorStats.size_bytes)"
    )
    Set-Content -Path (Join-Path $MirrorRoot "PUBLIC_REPO_STATE.md") -Value $stateMd -Encoding UTF8

    $syncStatus = [ordered]@{
        run_id = "fast-resume-" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
        status = $Status
        stage = $Stage
        engineering_ready = $EngineeringReady
        sync_time_utc = $syncTime
        mirror_stats = $MirrorStats
    }
    $syncStatus | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $MirrorRoot "PUBLIC_SYNC_STATUS.json") -Encoding UTF8

    $syncMd = @(
        "# Public Sync Status",
        "",
        "- status: $Status",
        "- stage: $Stage",
        "- engineering_ready: $EngineeringReady",
        "- sync_time_utc: $syncTime"
    )
    Set-Content -Path (Join-Path $MirrorRoot "PUBLIC_SYNC_STATUS.md") -Value $syncMd -Encoding UTF8

    $entryMd = @(
        "# Public Entrypoints",
        "",
        "1. README.md",
        "2. docs/CURRENT_PLATFORM_STATE.md",
        "3. docs/NEXT_CANONICAL_STEP.md",
        "4. workspace_config/workspace_manifest.json",
        "5. workspace_config/codex_manifest.json",
        "6. workspace_config/TASK_RULES.md"
    )
    Set-Content -Path (Join-Path $MirrorRoot "PUBLIC_ENTRYPOINTS.md") -Value $entryMd -Encoding UTF8
}

$sourceRoot = Resolve-SourceRepo
$repoName = Resolve-RepoName $sourceRoot
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}
if ([string]::IsNullOrWhiteSpace($ExcludesFilePath)) {
    $ExcludesFilePath = Join-Path $sourceRoot "setup_reports/public_mirror_excludes.txt"
}

$sourceRoot = [System.IO.Path]::GetFullPath($sourceRoot).TrimEnd("\")
$mirrorRoot = [System.IO.Path]::GetFullPath($MirrorPath).TrimEnd("\")
$excludesPath = [System.IO.Path]::GetFullPath($ExcludesFilePath)

if ($mirrorRoot.StartsWith($sourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Mirror must be outside source repo. source=$sourceRoot mirror=$mirrorRoot"
}
if ($mirrorRoot -match "\\tools(\\|$)") {
    throw "Mirror cannot be inside tools path. mirror=$mirrorRoot"
}

Ensure-Directory (Split-Path $mirrorRoot -Parent)
Ensure-Directory $mirrorRoot
Ensure-Directory (Join-Path $sourceRoot "setup_reports")

$excludes = Load-Excludes $excludesPath
$classified = Classify-ExcludeRules -Rules $excludes -SourceRoot $sourceRoot

$heavyDeferredDirs = @(
    (Join-Path $sourceRoot "runtime"),
    (Join-Path $sourceRoot "setup_assets")
)
$heavyDeferredDirs = @($heavyDeferredDirs | Where-Object { Test-Path $_ } | Sort-Object -Unique)

$progressJson = Join-Path $sourceRoot "setup_reports/public_mirror_progress_status.json"
$progressMd = Join-Path $sourceRoot "setup_reports/public_mirror_progress_status.md"
$stageLogsDir = Join-Path $sourceRoot "setup_reports/public_mirror_logs"
Ensure-Directory $stageLogsDir

$progress = [ordered]@{
    mode = "FAST_RESUME"
    source_path = $sourceRoot
    mirror_path = $mirrorRoot
    engineering_ready = $false
    current_stage = "INIT"
    status = "IN_PROGRESS"
    stage_results = (New-Object System.Collections.Generic.List[object])
    heavy_deferred_paths = @($heavyDeferredDirs | ForEach-Object { $_.Replace("\", "/") })
    updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
}

Write-ProgressStatus -ProgressObject $progress -JsonPath $progressJson -MdPath $progressMd

# STAGE A: fast usable mirror
$progress.current_stage = "STAGE_A_USABLE"
$stageAResults = New-Object System.Collections.Generic.List[object]
$keyDirs = @("docs", "workspace_config", "scripts", "projects", "setup_reports", "shared_systems")

foreach ($d in $keyDirs) {
    $src = Join-Path $sourceRoot $d
    if (-not (Test-Path $src)) { continue }
    $dst = Join-Path $mirrorRoot $d
    $logPath = Join-Path $stageLogsDir ("stageA_" + $d + ".log")
    $result = Invoke-RoboCopyStage -Label ("STAGE_A_" + $d) -Src $src -Dst $dst `
        -BaseExcludeDirs $classified.exclude_dirs -BaseExcludeFiles $classified.exclude_files `
        -ExtraExcludeDirs @() -ExtraExcludeFiles @() `
        -TimeBudgetSeconds ([Math]::Max(30, [Math]::Floor($StageATimeBudgetSeconds / [Math]::Max(1, $keyDirs.Count)))) `
        -LogPath $logPath
    $stageAResults.Add($result)
}

# root files
$rootPatterns = @("README*", ".gitignore")
$mirrorRootFiles = Get-ChildItem -Path $mirrorRoot -File -Force -ErrorAction SilentlyContinue
$sourceRootFiles = Get-ChildItem -Path $sourceRoot -File -Force -ErrorAction SilentlyContinue
$selectedSource = @()
foreach ($f in $sourceRootFiles) {
    foreach ($pat in $rootPatterns) {
        if ($f.Name -like $pat) {
            $selectedSource += $f
            break
        }
    }
}
foreach ($sf in $selectedSource) {
    Copy-Item -Path $sf.FullName -Destination (Join-Path $mirrorRoot $sf.Name) -Force
}
foreach ($mf in $mirrorRootFiles) {
    $matched = $false
    foreach ($pat in $rootPatterns) {
        if ($mf.Name -like $pat) { $matched = $true; break }
    }
    if ($matched -and -not (Test-Path (Join-Path $sourceRoot $mf.Name))) {
        Remove-Item -Path $mf.FullName -Force -ErrorAction SilentlyContinue
    }
}

$stageAStatus = if (($stageAResults | Where-Object { $_.status -eq "FAIL" }).Count -eq 0) { "PASS" } else { "PASS_WITH_WARNINGS" }
$mirrorStatsAfterA = Get-MirrorStats $mirrorRoot
$engineeringReady = (Test-Path (Join-Path $mirrorRoot "README.md")) -and `
    (Test-Path (Join-Path $mirrorRoot "docs")) -and `
    (Test-Path (Join-Path $mirrorRoot "workspace_config")) -and `
    (Test-Path (Join-Path $mirrorRoot "scripts")) -and `
    (Test-Path (Join-Path $mirrorRoot "projects"))

Write-PublicStateFiles -SourceRoot $sourceRoot -MirrorRoot $mirrorRoot -Excludes $excludes `
    -Stage "STAGE_A_USABLE" -EngineeringReady $engineeringReady -Status $stageAStatus -MirrorStats $mirrorStatsAfterA

$progress.engineering_ready = $engineeringReady
foreach ($r in $stageAResults) {
    $progress.stage_results.Add($r) | Out-Null
}
$progress.current_stage = "STAGE_B_INCREMENTAL"
$progress.updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
Write-ProgressStatus -ProgressObject $progress -JsonPath $progressJson -MdPath $progressMd

# STAGE B: incremental pass without heavy tail blocking
$stageBLog = Join-Path $stageLogsDir "stageB_incremental.log"
$stageB = Invoke-RoboCopyStage -Label "STAGE_B_INCREMENTAL" -Src $sourceRoot -Dst $mirrorRoot `
    -BaseExcludeDirs $classified.exclude_dirs -BaseExcludeFiles $classified.exclude_files `
    -ExtraExcludeDirs $heavyDeferredDirs -ExtraExcludeFiles @() `
    -TimeBudgetSeconds $StageBTimeBudgetSeconds -LogPath $stageBLog
$progress.stage_results.Add($stageB) | Out-Null

$mirrorStatsAfterB = Get-MirrorStats $mirrorRoot
Write-PublicStateFiles -SourceRoot $sourceRoot -MirrorRoot $mirrorRoot -Excludes $excludes `
    -Stage "STAGE_B_INCREMENTAL" -EngineeringReady $engineeringReady -Status $stageB.status -MirrorStats $mirrorStatsAfterB

$progress.current_stage = if ($RunHeavyTail) { "STAGE_C_HEAVY_TAIL" } else { "COMPLETE_FAST_MODE" }
$progress.updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
Write-ProgressStatus -ProgressObject $progress -JsonPath $progressJson -MdPath $progressMd

if ($RunHeavyTail) {
    foreach ($h in $heavyDeferredDirs) {
        if (-not (Test-Path $h)) { continue }
        $leaf = Split-Path $h -Leaf
        $dst = Join-Path $mirrorRoot $leaf
        $logPath = Join-Path $stageLogsDir ("stageC_" + $leaf + ".log")
        $stageC = Invoke-RoboCopyStage -Label ("STAGE_C_" + $leaf) -Src $h -Dst $dst `
            -BaseExcludeDirs $classified.exclude_dirs -BaseExcludeFiles $classified.exclude_files `
            -ExtraExcludeDirs @() -ExtraExcludeFiles @() `
            -TimeBudgetSeconds $StageCTimeBudgetSeconds -LogPath $logPath
        $progress.stage_results.Add($stageC) | Out-Null
    }
    $progress.current_stage = "COMPLETE_WITH_HEAVY_TAIL"
    $progress.updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    Write-ProgressStatus -ProgressObject $progress -JsonPath $progressJson -MdPath $progressMd
}

$finalStats = Get-MirrorStats $mirrorRoot
$anyFail = ($progress.stage_results | Where-Object { $_.status -eq "FAIL" }).Count -gt 0
$progress.status = if ($anyFail) { "PASS_WITH_WARNINGS" } else { "PASS" }
$progress.mirror_stats = $finalStats
$progress.updated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
Write-ProgressStatus -ProgressObject $progress -JsonPath $progressJson -MdPath $progressMd

Write-Host "[public-mirror-fast] source: $sourceRoot"
Write-Host "[public-mirror-fast] mirror: $mirrorRoot"
Write-Host "[public-mirror-fast] engineering_ready: $engineeringReady"
Write-Host "[public-mirror-fast] final_status: $($progress.status)"
Write-Host "[public-mirror-fast] progress_json: $progressJson"
