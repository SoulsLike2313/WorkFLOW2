$ErrorActionPreference = "Stop"

param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectSlug,
    [ValidateSet("user", "developer", "update", "verify", "main")]
    [string]$Entrypoint = "user",
    [int]$MainIndex = 0,
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed",
    [string]$StartupKind = "startup"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

& python .\scripts\project_startup.py run `
    --project-slug $ProjectSlug `
    --entrypoint $Entrypoint `
    --main-index $MainIndex `
    --port-mode $PortMode `
    --startup-kind $StartupKind

exit $LASTEXITCODE
