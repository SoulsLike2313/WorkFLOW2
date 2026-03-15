param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [int]$StageATimeBudgetSeconds = 180,
    [int]$StageBTimeBudgetSeconds = 180,
    [int]$StageCTimeBudgetSeconds = 600,
    [switch]$RunHeavyTail
)

$ErrorActionPreference = "Stop"

function Resolve-SourceRoot {
    if (-not [string]::IsNullOrWhiteSpace($SourceRepoPath)) {
        return (Resolve-Path $SourceRepoPath).Path
    }
    return (Resolve-Path ((git rev-parse --show-toplevel).Trim())).Path
}

$sourceRoot = Resolve-SourceRoot
$checkpointPath = Join-Path $sourceRoot "setup_reports/public_mirror_resume_checkpoint.json"

if ([string]::IsNullOrWhiteSpace($MirrorPath) -and (Test-Path $checkpointPath)) {
    try {
        $checkpoint = Get-Content -Raw $checkpointPath | ConvertFrom-Json
        if (-not [string]::IsNullOrWhiteSpace($checkpoint.mirror_path)) {
            $MirrorPath = $checkpoint.mirror_path
        }
    }
    catch {}
}

if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $repoName = [System.IO.Path]::GetFileName($sourceRoot)
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}

if ([string]::IsNullOrWhiteSpace($ExcludesFilePath)) {
    $ExcludesFilePath = Join-Path $sourceRoot "setup_reports/public_mirror_excludes.txt"
}

$MirrorPath = [System.IO.Path]::GetFullPath($MirrorPath).TrimEnd("\")
$sourceNorm = [System.IO.Path]::GetFullPath($sourceRoot).TrimEnd("\")
if ($MirrorPath.StartsWith($sourceNorm, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Resume refused: mirror path is inside source repo ($MirrorPath)."
}
if (-not (Test-Path $MirrorPath)) {
    throw "Resume refused: mirror path does not exist ($MirrorPath)."
}

$fastScript = Join-Path $sourceRoot "tools/public_mirror/fast_resume_public_mirror.ps1"
if (-not (Test-Path $fastScript)) {
    throw "fast_resume_public_mirror.ps1 not found: $fastScript"
}

$args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $fastScript,
    "-SourceRepoPath", $sourceRoot,
    "-MirrorPath", $MirrorPath,
    "-ExcludesFilePath", $ExcludesFilePath,
    "-StageATimeBudgetSeconds", $StageATimeBudgetSeconds,
    "-StageBTimeBudgetSeconds", $StageBTimeBudgetSeconds,
    "-StageCTimeBudgetSeconds", $StageCTimeBudgetSeconds
)
if ($RunHeavyTail) {
    $args += "-RunHeavyTail"
}

& powershell @args
