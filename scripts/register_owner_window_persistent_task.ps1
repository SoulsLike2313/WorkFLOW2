param(
    [string]$TaskName = "CVVCODEX_OwnerWindow_Localhost_Autostart_V1",
    [string]$ConfigPath = "runtime/factory_observation/owner_window_persistent_runtime_config_v1.json",
    [switch]$RunNow
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$launcherPath = Join-Path $PSScriptRoot "owner_window_persistent_launch.ps1"

if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "Launcher script not found: $launcherPath"
}

$configFullPath = if ([System.IO.Path]::IsPathRooted($ConfigPath)) {
    [System.IO.Path]::GetFullPath($ConfigPath)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $repoRoot $ConfigPath))
}

if (-not (Test-Path -LiteralPath $configFullPath)) {
    throw "Runtime config not found: $configFullPath"
}

$userId = "$env:USERDOMAIN\$env:USERNAME"
$powershellExe = Join-Path $PSHOME "powershell.exe"
$actionArguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launcherPath`" -ConfigPath `"$configFullPath`""

$action = New-ScheduledTaskAction -Execute $powershellExe -Argument $actionArguments -WorkingDirectory $repoRoot
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $userId
$settings = New-ScheduledTaskSettingsSet `
    -MultipleInstances IgnoreNew `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "CVVCODEX owner window localhost runtime autostart (ONLOGON)." `
    -Force | Out-Null

# Keep task name synchronized in runtime config for evidence and operator visibility.
$config = Get-Content -Path $configFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
$config.task_name = $TaskName
($config | ConvertTo-Json -Depth 8) | Set-Content -Path $configFullPath -Encoding UTF8

if ($RunNow.IsPresent) {
    Start-ScheduledTask -TaskName $TaskName
}

$task = Get-ScheduledTask -TaskName $TaskName
Write-Host "Owner window persistent task registered."
Write-Host "TaskName: $($task.TaskName)"
Write-Host "User: $userId"
Write-Host "Trigger: ONLOGON"
Write-Host "RunNow: $($RunNow.IsPresent)"
Write-Host "Launcher: $launcherPath"
Write-Host "Config: $configFullPath"
