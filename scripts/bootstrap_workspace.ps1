param(
    [string]$RepoRoot = "",
    [switch]$SetupActive,
    [switch]$SkipDependencyInstall
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}

Set-Location $RepoRoot

$workspaceManifestPath = Join-Path $RepoRoot "workspace_config\workspace_manifest.json"
$codexManifestPath = Join-Path $RepoRoot "workspace_config\codex_manifest.json"
$reportDir = Join-Path $RepoRoot "runtime\workspace_bootstrap"
New-Item -ItemType Directory -Path $reportDir -Force | Out-Null

$errors = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$projectChecks = New-Object System.Collections.Generic.List[object]
$setupActions = New-Object System.Collections.Generic.List[object]

if (-not (Test-Path $workspaceManifestPath)) {
    $errors.Add("Missing workspace manifest: $workspaceManifestPath")
}
if (-not (Test-Path $codexManifestPath)) {
    $errors.Add("Missing codex manifest: $codexManifestPath")
}

$workspaceManifestData = $null
$codex = $null

if ($errors.Count -eq 0) {
    try {
        $workspaceManifestData = Get-Content -Raw $workspaceManifestPath | ConvertFrom-Json
    }
    catch {
        $errors.Add("Invalid workspace manifest JSON: $($_.Exception.Message)")
    }

    try {
        $codex = Get-Content -Raw $codexManifestPath | ConvertFrom-Json
    }
    catch {
        $errors.Add("Invalid codex manifest JSON: $($_.Exception.Message)")
    }
}

$allowedStatuses = @("active", "supporting", "experimental", "archived", "legacy")
$activeProjects = @()

if ($null -ne $workspaceManifestData -and $errors.Count -eq 0) {
    foreach ($project in @($workspaceManifestData.projects)) {
        $projectPath = Join-Path $RepoRoot $project.path
        $manifestPath = Join-Path $RepoRoot $project.manifest_path
        $statusValid = $allowedStatuses -contains $project.status
        $pathExists = Test-Path $projectPath
        $manifestExists = Test-Path $manifestPath

        if (-not $statusValid) {
            $errors.Add("Project '$($project.project_id)' has invalid status '$($project.status)'.")
        }
        if (-not $pathExists) {
            $errors.Add("Project path missing for '$($project.project_id)': $($project.path)")
        }
        if (-not $manifestExists) {
            $errors.Add("Project manifest missing for '$($project.project_id)': $($project.manifest_path)")
        }

        if ($project.status -eq "active") {
            $activeProjects += $project
        }

        $projectChecks.Add([ordered]@{
            project_id = $project.project_id
            status = $project.status
            path = $project.path
            path_exists = $pathExists
            manifest_path = $project.manifest_path
            manifest_exists = $manifestExists
            status_valid = $statusValid
        })
    }

    $resolvedActive = @($workspaceManifestData.projects | Where-Object { $_.project_id -eq $workspaceManifestData.active_project_id })
    if ($resolvedActive.Count -ne 1) {
        $errors.Add("active_project_id '$($workspaceManifestData.active_project_id)' does not resolve uniquely.")
    }
    elseif ($resolvedActive[0].status -ne "active") {
        $errors.Add("active_project_id '$($workspaceManifestData.active_project_id)' is not marked as active.")
    }

    foreach ($bucket in $allowedStatuses) {
        if (-not $workspaceManifestData.status_index.PSObject.Properties.Name.Contains($bucket)) {
            $warnings.Add("status_index bucket missing: $bucket")
            continue
        }

        $bucketIds = @($workspaceManifestData.status_index.$bucket)
        foreach ($bucketId in $bucketIds) {
            $match = @($workspaceManifestData.projects | Where-Object { $_.project_id -eq $bucketId -and $_.status -eq $bucket })
            if ($match.Count -eq 0) {
                $errors.Add("status_index mismatch: '$bucketId' listed under '$bucket' but no matching project entry.")
            }
        }
    }
}

if ($SetupActive -and $errors.Count -eq 0) {
    foreach ($project in $activeProjects) {
        $projectRoot = Join-Path $RepoRoot $project.path
        $projectManifestPath = Join-Path $RepoRoot $project.manifest_path
        $projectManifest = $null

        try {
            $projectManifest = Get-Content -Raw $projectManifestPath | ConvertFrom-Json
        }
        catch {
            $errors.Add("Failed to parse project manifest for '$($project.project_id)': $($_.Exception.Message)")
            continue
        }

        $venvPath = Join-Path $projectRoot $projectManifest.bootstrap.venv_path
        $requirementsFile = if ([string]::IsNullOrWhiteSpace($projectManifest.bootstrap.requirements_file)) {
            Join-Path $projectRoot "requirements.txt"
        }
        else {
            Join-Path $projectRoot $projectManifest.bootstrap.requirements_file
        }

        if (-not (Test-Path $venvPath)) {
            Push-Location $projectRoot
            try {
                python -m venv $projectManifest.bootstrap.venv_path
                $setupActions.Add([ordered]@{
                    project_id = $project.project_id
                    action = "create_venv"
                    status = "done"
                    target = $projectManifest.bootstrap.venv_path
                })
            }
            catch {
                $errors.Add("Failed to create venv for '$($project.project_id)': $($_.Exception.Message)")
            }
            finally {
                Pop-Location
            }
        }
        else {
            $setupActions.Add([ordered]@{
                project_id = $project.project_id
                action = "create_venv"
                status = "skipped_existing"
                target = $projectManifest.bootstrap.venv_path
            })
        }

        if (-not $SkipDependencyInstall) {
            if (Test-Path $requirementsFile) {
                $pythonExe = Join-Path $venvPath "Scripts\python.exe"
                if (-not (Test-Path $pythonExe)) {
                    $warnings.Add("Python executable not found in venv for '$($project.project_id)': $pythonExe")
                }
                else {
                    Push-Location $projectRoot
                    try {
                        & $pythonExe -m pip install -r $requirementsFile
                        $setupActions.Add([ordered]@{
                            project_id = $project.project_id
                            action = "install_requirements"
                            status = "done"
                            target = (Split-Path -Leaf $requirementsFile)
                        })
                    }
                    catch {
                        $errors.Add("Dependency installation failed for '$($project.project_id)': $($_.Exception.Message)")
                    }
                    finally {
                        Pop-Location
                    }
                }
            }
            else {
                $warnings.Add("Requirements file not found for '$($project.project_id)': $requirementsFile")
            }
        }
        else {
            $setupActions.Add([ordered]@{
                project_id = $project.project_id
                action = "install_requirements"
                status = "skipped_by_flag"
                target = (Split-Path -Leaf $requirementsFile)
            })
        }
    }
}

$status = if ($errors.Count -eq 0) { if ($warnings.Count -eq 0) { "PASS" } else { "PASS_WITH_WARNINGS" } } else { "FAIL" }
$timestamp = Get-Date -Format "yyyyMMddTHHmmss"
$reportPath = Join-Path $reportDir "bootstrap_report_$timestamp.json"
$activeProjectId = ""
$projectCount = 0
if ($null -ne $workspaceManifestData -and $null -ne $workspaceManifestData.projects) {
    $projectCount = [int]@($workspaceManifestData.projects).Count
}
if ($null -ne $workspaceManifestData -and $null -ne $workspaceManifestData.active_project_id) {
    $activeProjectId = [string]$workspaceManifestData.active_project_id
}

$report = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    repo_root = $RepoRoot
    workspace_manifest = "workspace_config/workspace_manifest.json"
    codex_manifest = "workspace_config/codex_manifest.json"
    status = $status
    setup_active = [bool]$SetupActive
    skip_dependency_install = [bool]$SkipDependencyInstall
    summary = [ordered]@{
        project_count = $projectCount
        active_project_id = $activeProjectId
        errors = $errors.Count
        warnings = $warnings.Count
    }
    checks = @($projectChecks)
    setup_actions = @($setupActions)
    errors = @($errors)
    warnings = @($warnings)
}

$report | ConvertTo-Json -Depth 8 | Set-Content -Path $reportPath -Encoding UTF8

Write-Host "[workspace-bootstrap] status: $status"
Write-Host "[workspace-bootstrap] report: $reportPath"
if ($warnings.Count -gt 0) {
    Write-Host "[workspace-bootstrap] warnings: $($warnings.Count)"
}
if ($errors.Count -gt 0) {
    Write-Host "[workspace-bootstrap] errors: $($errors.Count)"
    exit 1
}

exit 0
