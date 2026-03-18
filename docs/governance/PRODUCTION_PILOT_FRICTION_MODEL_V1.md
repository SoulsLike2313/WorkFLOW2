# PRODUCTION_PILOT_FRICTION_MODEL_V1

## Purpose
Capture operational cost of mission execution during pilot without introducing heavy analytics infrastructure.

## Friction Dimensions
1. manual_steps_count
- definition: number of manual operator steps required beyond normal mission invocation.
- capture target: integer per mission.

2. repeated_check_burden
- definition: repeated executions of the same validation gate due unclear or stale state.
- capture target: integer + short cause note.

3. status_surface_clarity
- definition: whether runtime status surfaces were sufficient for operator decision.
- values: `CLEAR`, `PARTIAL`, `UNCLEAR`.

4. proof_discovery_difficulty
- definition: effort to locate required proof artifacts.
- values: `LOW`, `MEDIUM`, `HIGH`.

5. admission_completion_friction
- definition: overhead between admission readiness and completion claim.
- values: `LOW`, `MEDIUM`, `HIGH`.

6. runtime_truth_freshness_issues
- definition: stale or out-of-order runtime truth affecting mission interpretation.
- capture target: `none` or list of issues.

7. narrative_overhead
- definition: extra explanatory overhead required due duplicated or unclear surfaces.
- values: `LOW`, `MEDIUM`, `HIGH`.

## Friction Scoring (Lightweight)
- `LOW`: no blocking impact, no repeated ambiguity.
- `MEDIUM`: recoverable overhead that slows closure but does not compromise evidence.
- `HIGH`: recurring ambiguity or check churn that threatens reliable closure.

## Capture Rules
- capture once per mission in pilot execution report.
- summarize aggregate friction at pilot close.
- do not convert friction score into automatic mission verdict override.

## Use Rule
Friction data is decision support for stabilization and hardening, not a replacement for constitutional gates.
