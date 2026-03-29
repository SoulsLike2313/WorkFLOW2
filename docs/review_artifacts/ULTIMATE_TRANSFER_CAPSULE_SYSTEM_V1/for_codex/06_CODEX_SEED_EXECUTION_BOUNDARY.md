# 06_CODEX_SEED_EXECUTION_BOUNDARY

Codex execution boundary in seed mode:

Allowed:
1. bounded repo delta execution
2. diagnostics/validation/smoke checks
3. review artifact and transfer package production
4. tracker-consistent mutable refresh

Forbidden:
1. direction invention
2. foundation rewrite without explicit canon change
3. line collapse (continuity/handoff/live)
4. fake completion or hidden blocker handling
5. authority/scope reinterpretation by assumption

Escalate to owner/GPT when:
- required choice has non-obvious consequences
- missing authoritative surface blocks safe continuation
- requested action exceeds bounded scope

Active work session guard:
1. start timer at beginning of each new chat
2. at hour 4 emit warning
3. at hour 5 ask owner checkpoint question before continuing long-chain execution
4. if no owner answer at hour 5, emit sync-and-relocation prompt automatically
