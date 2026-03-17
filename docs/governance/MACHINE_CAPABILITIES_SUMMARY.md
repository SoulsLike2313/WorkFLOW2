# MACHINE_CAPABILITIES_SUMMARY

## Machine can
- Detect current machine mode.
- Validate sync/trust/governance/admission/evolution gates.
- Generate runtime status artifacts.
- Generate one-screen human-readable status.
- Validate integration inbox readiness.

## Machine cannot
- Canonically accept changes in helper mode.
- Override governance gates.
- Ignore sync drift or dirty worktree for acceptance gates.

## Machine is allowed to
- Report clear gate verdicts.
- Block unsafe progression.
- Propose next step from canonical routing.

## Machine is not allowed to
- Claim PASS when hard gates are failing.
- Treat role limitations as governance pass.
- Hide blockers.

## Machine reports
- trust verdict
- sync verdict
- governance verdict
- governance acceptance
- admission verdict
- evolution verdict
- machine mode and authority state
- next canonical step

## Machine blocks when
- sync is not `IN_SYNC`
- governance is non-compliant
- admission is rejected
- creator-only gate is requested without creator authority

## Machine hands off
- Runtime reports for audit-safe review.
- Structured one-screen snapshot for operator decisions.

## Machine confirms
- Current mode and authority visibility.
- Which gate is failing and why.
- What operator should do next.
