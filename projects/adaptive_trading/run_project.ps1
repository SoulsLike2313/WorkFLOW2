param(
    [ValidateSet("user", "developer", "train", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$repoRoot = Resolve-Path (Join-Path $projectRoot "..\..")
$startupScript = Join-Path $repoRoot "scripts\project_startup.py"

$startupRaw = & python $startupScript prepare --project-slug adaptive_trading --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for adaptive_trading."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

if ($Mode -eq "verify") {
    & python -m py_compile adaptive_trading_bot.py adaptive_trading_gui.py adaptive_trading_gui_easy.py adaptive_trading_gui_ultra.py
    exit $LASTEXITCODE
}

if ($Mode -eq "developer") {
    & python .\adaptive_trading_bot.py
    exit $LASTEXITCODE
}

if ($Mode -eq "train") {
    & python .\adaptive_trading_bot.py --mode train
    exit $LASTEXITCODE
}

& python .\adaptive_trading_gui.py
exit $LASTEXITCODE
