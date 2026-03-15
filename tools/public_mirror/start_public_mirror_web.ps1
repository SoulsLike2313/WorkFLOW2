param(
    [string]$SourceRepoPath,
    [string]$MirrorPath,
    [int]$Port = 18080,
    [string]$BindAddress = "0.0.0.0",
    [switch]$ForceRestart
)

$ErrorActionPreference = "Stop"

function Resolve-SourceRoot {
    if (-not [string]::IsNullOrWhiteSpace($SourceRepoPath)) {
        return (Resolve-Path $SourceRepoPath).Path
    }
    return (Resolve-Path ((git rev-parse --show-toplevel).Trim())).Path
}

function Resolve-RepoName([string]$RepoRoot) {
    $remote = (git -C $RepoRoot remote get-url origin 2>$null)
    if (-not [string]::IsNullOrWhiteSpace($remote)) {
        $leaf = Split-Path $remote -Leaf
        if ($leaf.EndsWith(".git")) {
            return [System.IO.Path]::GetFileNameWithoutExtension($leaf)
        }
        return $leaf
    }
    return [System.IO.Path]::GetFileName($RepoRoot)
}

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Read-RuntimeState([string]$PathValue) {
    if (Test-Path $PathValue) {
        try {
            $obj = Get-Content -Raw $PathValue | ConvertFrom-Json
            $hash = @{}
            if ($obj -ne $null) {
                foreach ($prop in $obj.PSObject.Properties) {
                    $hash[$prop.Name] = $prop.Value
                }
            }
            return $hash
        }
        catch {}
    }
    return @{}
}

function Write-RuntimeState([string]$PathValue, [hashtable]$Patch) {
    $state = Read-RuntimeState $PathValue
    foreach ($k in $Patch.Keys) {
        $state[$k] = $Patch[$k]
    }
    $state["updated_at_utc"] = (Get-Date).ToUniversalTime().ToString("o")
    $state | ConvertTo-Json -Depth 12 | Set-Content -Path $PathValue -Encoding UTF8
}

function Test-WebReady([string]$Url, [int]$TimeoutSeconds = 20) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {}
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Resolve-CaddyExecutable {
    $cmd = Get-Command caddy -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    foreach ($candidate in @(
            "C:\Users\PC\AppData\Local\Microsoft\WinGet\Links\caddy.exe",
            "C:\Program Files\Caddy\caddy.exe",
            "C:\ProgramData\chocolatey\bin\caddy.exe"
        )) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    return $null
}

$sourceRoot = Resolve-SourceRoot
$repoName = Resolve-RepoName $sourceRoot
if ([string]::IsNullOrWhiteSpace($MirrorPath)) {
    $MirrorPath = Join-Path (Join-Path (Split-Path $sourceRoot -Parent) "_public_repo_mirror") $repoName
}

$sourceRoot = [System.IO.Path]::GetFullPath($sourceRoot).TrimEnd("\")
$mirrorRoot = [System.IO.Path]::GetFullPath($MirrorPath).TrimEnd("\")
if ($mirrorRoot.StartsWith($sourceRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Mirror path must be outside source repo: $mirrorRoot"
}
if (-not (Test-Path $mirrorRoot)) {
    throw "Mirror path not found: $mirrorRoot"
}

$caddyExe = Resolve-CaddyExecutable
if ([string]::IsNullOrWhiteSpace($caddyExe)) {
    throw "Caddy executable not found. Install Caddy before starting canonical local web."
}

$runtimeDir = Join-Path $sourceRoot "setup_reports"
Ensure-Directory $runtimeDir
$runtimePath = Join-Path $runtimeDir "public_runtime_state.json"
$outLog = Join-Path $runtimeDir "public_server_stdout.log"
$errLog = Join-Path $runtimeDir "public_server_stderr.log"
$localUrl = "http://127.0.0.1:$Port/"

$state = Read-RuntimeState $runtimePath
$existingPid = 0
if ($state.ContainsKey("local_server_pid") -and $state["local_server_pid"]) {
    $existingPid = [int]$state["local_server_pid"]
}
if ($existingPid -gt 0) {
    $existingProcess = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
    if ($existingProcess) {
        if (-not $ForceRestart -and (Test-WebReady -Url $localUrl -TimeoutSeconds 3) -and ($state["local_server_type"] -eq "caddy")) {
            Write-Host "[public-mirror-web] already running caddy pid=$existingPid url=$localUrl"
            exit 0
        }
        Stop-Process -Id $existingPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 300
    }
}

$caddyConfigPath = Join-Path $sourceRoot "tools/public_mirror/Caddyfile"
$mirrorForCaddy = ($mirrorRoot -replace "\\", "/")
$caddyfile = @"
{
    admin off
    auto_https off
    persist_config off
}

$BindAddress`:$Port {
    root * $mirrorForCaddy
    @sensitive path /.git* /.env /.env.* /id_rsa* /id_ed25519* /*.pem /*.key /*.pfx /*.p12 /secrets.* /token* /credentials*
    respond @sensitive 404
    file_server browse {
        hide .git .env .env.* *.pem *.key *.pfx *.p12 id_rsa id_ed25519 secrets.* token* credentials*
    }
}
"@
Set-Content -Path $caddyConfigPath -Value $caddyfile -Encoding UTF8

Set-Content -Path $outLog -Value "" -Encoding UTF8
Set-Content -Path $errLog -Value "" -Encoding UTF8

$args = @("run", "--config", $caddyConfigPath, "--adapter", "caddyfile")
$proc = Start-Process -FilePath $caddyExe -ArgumentList $args -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog

$ready = Test-WebReady -Url $localUrl -TimeoutSeconds 20
if (-not $ready) {
    try { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue } catch {}
    throw "Caddy local web failed to start on $localUrl"
}

Write-RuntimeState -PathValue $runtimePath -Patch ([ordered]@{
        source_repo_path = $sourceRoot
        mirror_path = $mirrorRoot
        caddy_config_path = $caddyConfigPath
        local_server_type = "caddy"
        local_server_pid = $proc.Id
        local_server_command = "$caddyExe $($args -join ' ')"
        local_server_started_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        local_url = $localUrl
        local_bind_address = $BindAddress
        local_bind_port = $Port
        canonical_local_hosting = "caddy_direct_local_pc"
        github_is_not_source_of_truth = $true
    })

Write-Host "[public-mirror-web] started caddy pid=$($proc.Id) url=$localUrl mirror=$mirrorRoot"
