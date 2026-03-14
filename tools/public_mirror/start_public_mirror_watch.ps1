param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [string]$ExcludesFilePath,
    [int]$DebounceSeconds = 3,
    [switch]$StartWeb,
    [switch]$StartTunnel,
    [int]$Port = 18080
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

$runtimeDir = Join-Path $SourceRepoPath "setup_reports"
Ensure-Directory $runtimeDir
$runtimeStatePath = Join-Path $runtimeDir "public_runtime_state.json"
$watchLogPath = Join-Path $runtimeDir "public_mirror_watch.log"
$serverOutPath = Join-Path $runtimeDir "public_server_stdout.log"
$serverErrPath = Join-Path $runtimeDir "public_server_stderr.log"
$tunnelOutPath = Join-Path $runtimeDir "public_tunnel_stdout.log"
$tunnelErrPath = Join-Path $runtimeDir "public_tunnel_stderr.log"

function Invoke-Sync([switch]$SkipManifest) {
    $syncScript = Join-Path $SourceRepoPath "tools/public_mirror/sync_repo_to_public_mirror.ps1"
    & powershell -NoProfile -ExecutionPolicy Bypass -File $syncScript `
        -SourceRepoPath $SourceRepoPath `
        -MirrorPath $MirrorPath `
        -ExcludesFilePath $ExcludesFilePath `
        -PublicRuntimeStatePath $runtimeStatePath `
        -SkipFileManifest:$SkipManifest `
        -Quiet
}

function Save-RuntimeState([hashtable]$StatePatch) {
    $state = @{}
    if (Test-Path $runtimeStatePath) {
        try {
            $state = Get-Content -Raw $runtimeStatePath | ConvertFrom-Json -AsHashtable
        }
        catch {
            $state = @{}
        }
    }
    foreach ($k in $StatePatch.Keys) {
        $state[$k] = $StatePatch[$k]
    }
    $state["updated_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
    $state | ConvertTo-Json -Depth 8 | Set-Content -Path $runtimeStatePath -Encoding UTF8
}

function Start-LocalWebServer {
    $args = @("-m", "http.server", "$Port", "--bind", "127.0.0.1", "--directory", "$MirrorPath")
    $proc = Start-Process -FilePath "python" -ArgumentList $args -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $serverOutPath -RedirectStandardError $serverErrPath
    Save-RuntimeState @{
        local_server_pid = $proc.Id
        local_url = "http://127.0.0.1:$Port/"
        local_server_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    }
    return $proc
}

function Start-PublicTunnel {
    $sshArgs = @(
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-o", "StrictHostKeyChecking=accept-new",
        "-R", "80:127.0.0.1:$Port",
        "nokey@localhost.run"
    )
    $proc = Start-Process -FilePath "ssh" -ArgumentList $sshArgs -PassThru -WindowStyle Hidden `
        -RedirectStandardOutput $tunnelOutPath -RedirectStandardError $tunnelErrPath
    Save-RuntimeState @{
        tunnel_pid = $proc.Id
        tunnel_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        tunnel_command = "ssh -R 80:127.0.0.1:$Port nokey@localhost.run"
    }

    $publicUrl = $null
    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Milliseconds 1000
        if (Test-Path $tunnelOutPath) {
            $text = Get-Content -Raw $tunnelOutPath
            $match = [regex]::Match($text, "https?://[a-zA-Z0-9\.\-/_]+")
            if ($match.Success) {
                $publicUrl = $match.Value.TrimEnd("/")
                break
            }
        }
        if ($proc.HasExited) {
            break
        }
    }
    if ($publicUrl) {
        Save-RuntimeState @{
            public_url = $publicUrl
            public_url_detected_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        }
    }
    return $proc
}

Add-Content -Path $watchLogPath -Value ("[{0}] watch start" -f (Get-Date).ToString("s"))
Invoke-Sync

$webProc = $null
$tunnelProc = $null
if ($StartWeb) {
    $webProc = Start-LocalWebServer
}
if ($StartTunnel) {
    $tunnelProc = Start-PublicTunnel
}

Save-RuntimeState @{
    watch_mode = "active"
    watch_pid = $PID
    source_repo_path = $SourceRepoPath
    mirror_path = $MirrorPath
    excludes_file_path = $ExcludesFilePath
    debounce_seconds = $DebounceSeconds
}

$script:pending = $false
$script:lastEvent = Get-Date

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $SourceRepoPath
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, DirectoryName, Size'

$onEvent = {
    if ($Event.SourceEventArgs.FullPath -match "\\\.git(\\|$)") {
        return
    }
    $script:pending = $true
    $script:lastEvent = Get-Date
}

$handlers = @(
    Register-ObjectEvent $watcher Changed -Action $onEvent,
    Register-ObjectEvent $watcher Created -Action $onEvent,
    Register-ObjectEvent $watcher Deleted -Action $onEvent,
    Register-ObjectEvent $watcher Renamed -Action $onEvent
)

try {
    while ($true) {
        Start-Sleep -Milliseconds 1000
        if ($script:pending -and ((Get-Date) -gt $script:lastEvent.AddSeconds($DebounceSeconds))) {
            $script:pending = $false
            Add-Content -Path $watchLogPath -Value ("[{0}] change detected -> sync" -f (Get-Date).ToString("s"))
            Invoke-Sync -SkipManifest
            Save-RuntimeState @{
                last_watch_sync_utc = (Get-Date).ToUniversalTime().ToString("o")
            }
        }
    }
}
finally {
    foreach ($h in $handlers) {
        Unregister-Event -SourceIdentifier $h.Name -ErrorAction SilentlyContinue
    }
    $watcher.Dispose()
    Add-Content -Path $watchLogPath -Value ("[{0}] watch stop" -f (Get-Date).ToString("s"))
    Save-RuntimeState @{
        watch_mode = "stopped"
    }
}
