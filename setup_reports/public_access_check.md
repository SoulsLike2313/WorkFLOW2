# Public Access Check

- checked_at_utc: 2026-03-15T14:43:44.8968145Z
- public_url: 
- public_access_provider: cloudflared_quick_tunnel
- public_access_mechanism: cloudflared quick tunnel (trycloudflare.com)
- public_access_vpn_dependent: False
- local_target_url: http://127.0.0.1:18080/
- tunnel_pid: 0
- tunnel_process_alive: False
- old_public_url: https://ac85f2bd6236a2.lhr.life
- old_broken_public_url: https://ac85f2bd6236a2.lhr.life
- old_broken_public_url_cause: stale_session_hostname_not_mapped
- latest_tunnel_url_from_logs: 
- runtime_url_outdated: False
- failure_cause: public_url_missing_in_runtime_state
- status: FAIL

## Checks

- public_url_present
```json
{
    "pass":  false,
    "reason":  "public_url_missing"
}
```
