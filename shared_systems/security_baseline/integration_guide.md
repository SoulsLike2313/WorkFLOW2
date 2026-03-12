# Security Baseline

Slug: $(System.Collections.Hashtable.slug)

Purpose:
- Reusable minimum security and configuration hygiene baseline

Status:
- maturity_level: $(System.Collections.Hashtable.maturity)

This module is portable and intended to be installed through:
- scripts/install_system.py

Removal must be executed through:
- scripts/remove_system.py
"@ | Set-Content -Path (Join-Path E:\CVVCODEX\shared_systems\security_baseline 'README.md') -Encoding UTF8

  @"
# Integration Guide: Security Baseline

## Integration Steps
1. Validate project compatibility using SYSTEM_MANIFEST.json.
2. Install via python scripts/install_system.py --project-slug <slug> --system-slug security_baseline.
3. Confirm project manifest updates (installed_systems, status, history).
4. Execute post-install checks from install summary.

## Uninstall Steps
1. Execute python scripts/remove_system.py --project-slug <slug> --system-slug security_baseline.
2. Confirm manifest detachment and remove summary.
3. Run verification/readiness checks for target project.
