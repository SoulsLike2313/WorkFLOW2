$ErrorActionPreference = "Stop"

param(
    [ValidateSet("user", "developer", "verify")]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed"
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$cursor = $projectRoot
$repoRoot = $null
while ($true) {
    if (Test-Path (Join-Path $cursor "workspace_config\workspace_manifest.json")) {
        $repoRoot = $cursor
        break
    }
    $parent = Split-Path -Parent $cursor
    if ($parent -eq $cursor) {
        throw "Unable to locate workspace root from project path: $projectRoot"
    }
    $cursor = $parent
}

$startupScript = Join-Path $repoRoot "scripts\project_startup.py"
$startupRaw = & python $startupScript prepare --project-slug game_ru_ai --startup-kind $Mode --port-mode $PortMode
if ($LASTEXITCODE -ne 0) {
    throw "Startup preflight failed for project: game_ru_ai"
}

$startup = $startupRaw | ConvertFrom-Json
$startup.env.PSObject.Properties | ForEach-Object {
    Set-Item -Path ("Env:" + $_.Name) -Value ([string]$_.Value)
}

$command = ""
if ($Mode -eq "user") {
    $command = "python -m app.main"
} elseif ($Mode -eq "developer") {
    $command = "python -m app.main"
} else {
    $command = "python -m pytest -q"
}

Invoke-Expression $command
exit $LASTEXITCODE

