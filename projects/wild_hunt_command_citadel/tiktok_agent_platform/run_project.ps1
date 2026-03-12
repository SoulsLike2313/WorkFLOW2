param(
    [ValidateSet(
        "user",
        "developer",
        "verify",
        "update",
        "core-user",
        "core-developer",
        "core-verify",
        "agent-user",
        "agent-developer",
        "agent-verify"
    )]
    [string]$Mode = "user",
    [ValidateSet("fixed", "auto")]
    [string]$PortMode = "fixed",
    [string]$ManifestPath = "",
    [string]$BundlePath = "",
    [string]$TargetVersion = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$coreRoot = Join-Path $projectRoot "core"
$agentRoot = Join-Path $projectRoot "agent"

if (-not (Test-Path $coreRoot)) {
    throw "Core layer directory not found: $coreRoot"
}
if (-not (Test-Path $agentRoot)) {
    throw "Agent layer directory not found: $agentRoot"
}

function Invoke-CoreRun {
    param(
        [string]$ScriptName,
        [hashtable]$Args = @{}
    )
    $scriptPath = Join-Path $coreRoot $ScriptName
    if (-not (Test-Path $scriptPath)) {
        throw "Core script not found: $scriptPath"
    }
    & powershell -ExecutionPolicy Bypass -File $scriptPath @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Core script failed: $ScriptName (exit $LASTEXITCODE)"
    }
}

function Invoke-AgentMode {
    param([string]$AgentMode)
    $scriptPath = Join-Path $agentRoot "run_project.ps1"
    if (-not (Test-Path $scriptPath)) {
        throw "Agent run script not found: $scriptPath"
    }
    & powershell -ExecutionPolicy Bypass -File $scriptPath -Mode $AgentMode -PortMode $PortMode
    if ($LASTEXITCODE -ne 0) {
        throw "Agent mode failed: $AgentMode (exit $LASTEXITCODE)"
    }
}

switch ($Mode) {
    "core-user" {
        Invoke-CoreRun -ScriptName "run_user.ps1" -Args @{ PortMode = $PortMode }
        exit 0
    }
    "core-developer" {
        Invoke-CoreRun -ScriptName "run_developer.ps1" -Args @{ PortMode = $PortMode }
        exit 0
    }
    "core-verify" {
        Invoke-CoreRun -ScriptName "run_verify.ps1" -Args @{ PortMode = $PortMode }
        exit 0
    }
    "agent-user" {
        Invoke-AgentMode -AgentMode "user"
        exit 0
    }
    "agent-developer" {
        Invoke-AgentMode -AgentMode "developer"
        exit 0
    }
    "agent-verify" {
        Invoke-AgentMode -AgentMode "verify"
        exit 0
    }
    "user" {
        Invoke-AgentMode -AgentMode "user"
        exit 0
    }
    "developer" {
        Invoke-AgentMode -AgentMode "developer"
        exit 0
    }
    "update" {
        $args = @{
            Mode = "check"
            PortMode = $PortMode
        }
        if (-not [string]::IsNullOrWhiteSpace($ManifestPath)) {
            $args["ManifestPath"] = $ManifestPath
        }
        if (-not [string]::IsNullOrWhiteSpace($BundlePath)) {
            $args["BundlePath"] = $BundlePath
        }
        if (-not [string]::IsNullOrWhiteSpace($TargetVersion)) {
            $args["TargetVersion"] = $TargetVersion
        }

        $updateMode = "check"
        if (-not [string]::IsNullOrWhiteSpace($BundlePath) -and -not [string]::IsNullOrWhiteSpace($TargetVersion)) {
            $updateMode = "apply"
        } elseif ([string]::IsNullOrWhiteSpace($ManifestPath) -and [string]::IsNullOrWhiteSpace($BundlePath)) {
            $updateMode = "post-verify"
        }
        $args["Mode"] = $updateMode
        Invoke-CoreRun -ScriptName "run_update.ps1" -Args $args
        exit 0
    }
    "verify" {
        Invoke-CoreRun -ScriptName "run_verify.ps1" -Args @{ PortMode = $PortMode }
        Invoke-AgentMode -AgentMode "verify"

        $pythonExe = Join-Path $coreRoot ".venv\Scripts\python.exe"
        $uiValidateScript = Join-Path $coreRoot "scripts\ui_validate.py"
        if ((Test-Path $pythonExe) -and (Test-Path $uiValidateScript)) {
            & $pythonExe $uiValidateScript --api-base-url "http://127.0.0.1:9"
            if ($LASTEXITCODE -ne 0) {
                throw "Core UI-QA validation failed (exit $LASTEXITCODE)."
            }
        }
        exit 0
    }
}
