# Public Access Check

- checked_at_utc: 2026-03-15T18:38:05.3251374Z
- local_target_url: http://127.0.0.1:18080/
- public_url: http://185.171.202.83:18080
- public_access_provider: direct_local_pc_caddy
- public_access_mechanism: direct local-PC hosting via Caddy (non-tunnel canonical)
- public_access_vpn_dependent: False
- session_based_url: False
- stability_classification: 
- stable_enough_for_chatgpt: 
- repeated_checks_passed: n/a/n/a
- manual_step_required: Create router NAT/port-forward rule
- exact_router_rule: TCP 18080 -> 192.168.0.27:18080
- post_step_verification_command: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/check_public_mirror_public_access.ps1 -SourceRepoPath E:\CVVCODEX -RunStabilitySeries -RootCheckCount 5 -FileCheckRounds 3 -IntervalSeconds 4
- failure_cause: router_port_forwarding_or_dns_mapping_not_configured
- status: FAIL

## Checks

- local_root_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- local_public_state_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- root_access
```json
{
    "ok":  false,
    "status":  null,
    "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
}
```

- state_file_access
```json
{
    "ok":  false,
    "status":  null,
    "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
}
```

- sync_status_file_access
```json
{
    "ok":  false,
    "status":  null,
    "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
}
```

- entrypoints_file_access
```json
{
    "ok":  false,
    "status":  null,
    "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
}
```

- git_path_blocked
```json
{
    "pass":  true,
    "probe":  {
                  "ok":  false,
                  "status":  null,
                  "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
              }
}
```

- env_path_blocked
```json
{
    "pass":  true,
    "probe":  {
                  "ok":  false,
                  "status":  null,
                  "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто."
              }
}
```
