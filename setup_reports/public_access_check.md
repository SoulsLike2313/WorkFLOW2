# Public Access Check

- checked_at_utc: 2026-03-15T17:39:23.4993814Z
- local_target_url: http://127.0.0.1:18080/
- public_url: 
- public_access_provider: direct_local_pc_caddy
- public_access_mechanism: direct local-PC hosting via Caddy (non-tunnel canonical)
- public_access_vpn_dependent: False
- session_based_url: False
- stability_classification: BROKEN
- stable_enough_for_chatgpt: False
- repeated_checks_passed: 0/0
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
