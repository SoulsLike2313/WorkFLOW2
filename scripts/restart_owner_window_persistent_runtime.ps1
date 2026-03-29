param(
    [string]$ConfigPath = "runtime/factory_observation/owner_window_persistent_runtime_config_v1.json"
)

$ErrorActionPreference = "Stop"

$launcherPath = Join-Path $PSScriptRoot "owner_window_persistent_launch.ps1"
if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "Launcher script not found: $launcherPath"
}

& $launcherPath -ConfigPath $ConfigPath -ForceRestart
