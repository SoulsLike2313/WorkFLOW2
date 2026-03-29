param(
  [string]$BundlePath = "runtime/chatgpt_bundle_exports/tiktok_wave1_tranche1_live_ongoing_checkpoint_manual_safe_bundle_latest.zip",
  [string]$Host = "127.0.0.1",
  [int]$Port = 8777
)

$repoRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
$scriptPath = Join-Path $repoRoot "shared_systems/factory_observation_window_v1/app/local_factory_observation_server.py"

python $scriptPath --bundle $BundlePath --host $Host --port $Port
