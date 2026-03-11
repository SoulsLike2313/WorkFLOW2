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

$workspace = $null
$codex = $null

if ($errors.Count -eq 0) {
    try {
        $workspace = Get-Content -Raw $workspaceManifestPath | ConvertFrom-Json
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

$registry = @()
$activeProjectSlug = ""
$allowedStatuses = @("active", "supporting", "experimental", "archived", "legacy")
$activeProject = $null

if ($null -ne $workspace -and $errors.Count -eq 0) {
    if ($workspace.status_values) {
        $allowedStatuses = @($workspace.status_values)
    }

    $activeProjectSlug = [string]$workspace.active_project
    $registry = @($workspace.project_registry)

    if ($registry.Count -eq 0) {
        $errors.Add("Workspace project_registry is empty.")
    }

    foreach ($project in $registry) {
        $slug = [string]$project.slug
        $status = [string]$project.status
        $rootRel = [string]$project.root_path
        $manifestRel = [string]$project.manifest_path
        $readmeRel = [string]$project.readme_path

        $rootPath = Join-Path $RepoRoot $rootRel
        $manifestPath = Join-Path $RepoRoot $manifestRel
        $readmePath = Join-Path $RepoRoot $readmeRel

        $statusValid = $allowedStatuses -contains $status
        $rootExists = Test-Path $rootPath
        $manifestExists = Test-Path $manifestPath
        $readmeExists = Test-Path $readmePath

        if (-not $statusValid) {
            $errors.Add("Project '$slug' has invalid status '$status'.")
        }
        if (-not $rootExists) {
            $errors.Add("Project '$slug' missing root_path '$rootRel'.")
        }
        if (-not $manifestExists) {
            $errors.Add("Project '$slug' missing manifest_path '$manifestRel'.")
        }
        if (-not $readmeExists) {
            $errors.Add("Project '$slug' missing readme_path '$readmeRel'.")
        }

        if ($manifestExists) {
            try {
                $projectManifest = Get-Content -Raw $manifestPath | ConvertFrom-Json
                $manifestSlug = [string]$projectManifest.slug
                $manifestStatus = [string]$projectManifest.status
                if ($manifestSlug -ne $slug) {
                    $errors.Add("Manifest slug mismatch for '$slug' (manifest has '$manifestSlug').")
                }
                if ($manifestStatus -ne $status) {
                    $errors.Add("Manifest status mismatch for '$slug': registry='$status', manifest='$manifestStatus'.")
                }
            }
            catch {
                $errors.Add("Project '$slug' manifest parse failed: $($_.Exception.Message)")
            }
        }

        if ($slug -eq $activeProjectSlug) {
            $activeProject = $project
            if ($status -ne "active") {
                $errors.Add("active_project '$activeProjectSlug' is not marked as status 'active'.")
            }
        }

        $projectChecks.Add([ordered]@{
            slug = $slug
            status = $status
            root_path = $rootRel
            root_exists = $rootExists
            manifest_path = $manifestRel
            manifest_exists = $manifestExists
            readme_path = $readmeRel
            readme_exists = $readmeExists
            status_valid = $statusValid
        })
    }

    if ($null -eq $activeProject) {
        $errors.Add("Could not resolve active_project '$activeProjectSlug' in project_registry.")
    }

    $activeCount = @($registry | Where-Object { [string]$_.status -eq "active" }).Count
    if ($activeCount -ne 1) {
        $errors.Add("Expected exactly one active project, found $activeCount.")
    }
}

if ($SetupActive -and $errors.Count -eq 0 -and $null -ne $activeProject) {
    $activeRootPath = Join-Path $RepoRoot ([string]$activeProject.root_path)
    $activeManifestPath = Join-Path $RepoRoot ([string]$activeProject.manifest_path)

    try {
        $manifest = Get-Content -Raw $activeManifestPath | ConvertFrom-Json
        $venvPath = Join-Path $activeRootPath ".venv"
        $depsRel = [string]$manifest.dependencies_file
        if ([string]::IsNullOrWhiteSpace($depsRel)) {
            $depsRel = "requirements.txt"
        }
        $depsPath = Join-Path $activeRootPath $depsRel

        if (-not (Test-Path $venvPath)) {
            Push-Location $activeRootPath
            try {
                python -m venv .venv
                $setupActions.Add([ordered]@{
                    slug = [string]$manifest.slug
                    action = "create_venv"
                    status = "done"
                    target = ".venv"
                })
            }
            catch {
                $errors.Add("Failed to create active project venv: $($_.Exception.Message)")
            }
            finally {
                Pop-Location
            }
        }
        else {
            $setupActions.Add([ordered]@{
                slug = [string]$manifest.slug
                action = "create_venv"
                status = "skipped_existing"
                target = ".venv"
            })
        }

        if (-not $SkipDependencyInstall) {
            if (Test-Path $depsPath) {
                $pythonExe = Join-Path $venvPath "Scripts\python.exe"
                if (Test-Path $pythonExe) {
                    Push-Location $activeRootPath
                    try {
                        & $pythonExe -m pip install -r $depsPath
                        $setupActions.Add([ordered]@{
                            slug = [string]$manifest.slug
                            action = "install_dependencies"
                            status = "done"
                            target = $depsRel
                        })
                    }
                    catch {
                        $errors.Add("Failed to install dependencies for active project: $($_.Exception.Message)")
                    }
                    finally {
                        Pop-Location
                    }
                }
                else {
                    $warnings.Add("Active project venv python not found: $pythonExe")
                }
            }
            else {
                $warnings.Add("Active project dependencies file not found: $depsPath")
            }
        }
        else {
            $setupActions.Add([ordered]@{
                slug = [string]$manifest.slug
                action = "install_dependencies"
                status = "skipped_by_flag"
                target = $depsRel
            })
        }
    }
    catch {
        $errors.Add("Failed setup for active project '$($activeProject.slug)': $($_.Exception.Message)")
    }
}

$status = if ($errors.Count -gt 0) { "FAIL" } elseif ($warnings.Count -gt 0) { "PASS_WITH_WARNINGS" } else { "PASS" }
$timestamp = Get-Date -Format "yyyyMMddTHHmmss"
$reportPath = Join-Path $reportDir "bootstrap_report_$timestamp.json"

$verificationCommand = ""
if ($null -ne $workspace -and $null -ne $workspace.verification_entrypoints) {
    $verificationCommand = [string]$workspace.verification_entrypoints.active_project_verify
}
if ([string]::IsNullOrWhiteSpace($verificationCommand)) {
    $verificationCommand = "python -m app.verify"
}

$activeEntryHints = @()
if ($null -ne $activeProject -and $null -ne $activeProject.main_entrypoints) {
    $activeEntryHints = @($activeProject.main_entrypoints)
}

$firstActionPlan = @(
    "Run workspace validation: python scripts/validate_workspace.py",
    "Open active project manifest and README",
    "Run active verification entrypoint",
    "Review latest verification artifacts before manual testing"
)

$report = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    repo_root = $RepoRoot
    workspace_manifest_path = "workspace_config/workspace_manifest.json"
    codex_manifest_path = "workspace_config/codex_manifest.json"
    status = $status
    active_project = $activeProjectSlug
    setup_active = [bool]$SetupActive
    skip_dependency_install = [bool]$SkipDependencyInstall
    summary = [ordered]@{
        project_count = $registry.Count
        warnings = $warnings.Count
        errors = $errors.Count
    }
    project_registry = @($projectChecks.ToArray())
    entrypoint_hints = [ordered]@{
        active_project_main_entrypoints = $activeEntryHints
        workspace_bootstrap = if ($null -ne $workspace) { [string]$workspace.entrypoints.workspace_bootstrap } else { "" }
        workspace_validator = if ($null -ne $workspace) { [string]$workspace.entrypoints.workspace_validate } else { "python scripts/validate_workspace.py" }
    }
    verification_command = $verificationCommand
    first_action_plan = $firstActionPlan
    setup_actions = @($setupActions.ToArray())
    warnings = @($warnings.ToArray())
    errors = @($errors.ToArray())
}

$report | ConvertTo-Json -Depth 10 | Set-Content -Path $reportPath -Encoding UTF8

Write-Host "[workspace-bootstrap] status: $status"
Write-Host "[workspace-bootstrap] active_project: $activeProjectSlug"
Write-Host "[workspace-bootstrap] report: $reportPath"

if ($errors.Count -gt 0) {
    exit 1
}
exit 0
