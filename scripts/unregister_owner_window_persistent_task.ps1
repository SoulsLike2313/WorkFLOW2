param(
    [string]$TaskName = "CVVCODEX_OwnerWindow_Localhost_Autostart_V1"
)

$ErrorActionPreference = "Stop"

Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
Write-Host "Owner window persistent task removed: $TaskName"
