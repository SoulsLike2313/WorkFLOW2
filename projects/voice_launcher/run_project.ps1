param(
    [ValidateSet("user", "developer", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$repoRoot = Resolve-Path (Join-Path $projectRoot "..\..")
$startupScript = Join-Path $repoRoot "scripts\project_startup.py"

$startupRaw = & python $startupScript prepare --project-slug voice_launcher --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for voice_launcher."
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

if ($Mode -eq "verify") {
    & python -m pytest -q
    exit $LASTEXITCODE
}

& python .\voice_launcher.py
exit $LASTEXITCODE
