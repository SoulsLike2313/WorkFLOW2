param(
    [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"
$storage = Join-Path $env:APPDATA "VoiceLauncher"
if (-not (Test-Path $storage)) {
    Write-Host "Storage folder not found: $storage"
    exit 1
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
if ([string]::IsNullOrWhiteSpace($OutDir)) {
    $base = Join-Path (Split-Path -Parent $PSScriptRoot) "dev_logs"
    $OutDir = Join-Path $base ("dump_" + $stamp)
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$files = @(
    "runtime.log",
    "runtime.log.1",
    "runtime.log.2",
    "asr_events.log",
    "asr_events.log.1",
    "launcher_automation.log",
    "dev_session_snapshot.json",
    "commands.json",
    "settings.json"
)

foreach ($name in $files) {
    $src = Join-Path $storage $name
    if (Test-Path $src) {
        Copy-Item $src -Destination (Join-Path $OutDir $name) -Force
    }
}

Write-Host "Logs collected to: $OutDir"
