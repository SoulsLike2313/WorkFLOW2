# Verification Toolkit

Slug: $(System.Collections.Hashtable.slug)

Purpose:
- Reusable verification gates and readiness checks

Status:
- maturity_level: $(System.Collections.Hashtable.maturity)

This module is portable and intended to be installed through:
- scripts/install_system.py

Removal must be executed through:
- scripts/remove_system.py
"@ | Set-Content -Path (Join-Path <REPO_ROOT>\shared_systems\verification_toolkit 'README.md') -Encoding UTF8

  @"
# Integration Guide: Verification Toolkit

## Integration Steps
1. Validate project compatibility using SYSTEM_MANIFEST.json.
2. Install via python scripts/install_system.py --project-slug <slug> --system-slug verification_toolkit.
3. Confirm project manifest updates (installed_systems, status, history).
4. Execute post-install checks from install summary.

## Uninstall Steps
1. Execute python scripts/remove_system.py --project-slug <slug> --system-slug verification_toolkit.
2. Confirm manifest detachment and remove summary.
3. Run verification/readiness checks for target project.
