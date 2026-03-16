# SECURITY AND EXPOSURE INCIDENT POLICY

Policy class: Governance v1.1 hardening security response control.

Authority inputs:

- `docs/repo_publication_policy.md`
- `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`

## 1) Unsafe public state definition

Unsafe public state includes any tracked safe mirror content containing:

1. secrets/credentials/tokens/keys
2. unsafe exposure diagnostics (WAN/LAN/router/tunnel)
3. prohibited sensitive artifacts
4. accidental private operational data

## 2) Incident scenarios

1. accidental commit of sensitive file
2. accidental commit of sensitive value inside allowed file
3. misclassified artifact included in public safe mirror
4. compromised public state where trust cannot be guaranteed

## 3) Immediate response steps

1. classify incident severity
2. freeze completion and promotion
3. identify affected commits and artifact paths
4. remove/replace unsafe content
5. push remediated safe state
6. rerun sync, trust, and security checks

## 4) Mirror freeze and rollback

Freeze required for confirmed exposure incidents.

Rollback target:

- last trusted safe commit before incident.

Rollback must include:

1. scope report (files, commits)
2. remediation commit
3. revalidation proof

## 5) Trusted restore conditions

Trusted restore allowed only if:

1. unsafe paths removed from tracked state
2. content scan has zero critical hits
3. sync parity restored
4. admission gate returns non-rejected status

## 6) Evidence requirements

Required evidence package:

1. incident timestamp and classification
2. affected paths and SHAs
3. remediation actions
4. post-fix check results
5. final trust verdict

## 7) Notification requirements

Mandatory notifications:

1. immediate blocker notification on incident detection
2. escalation notice for critical incidents
3. restore notice with evidence summary after remediation