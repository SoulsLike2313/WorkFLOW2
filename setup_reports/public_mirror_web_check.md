# Public Mirror Web Check (Inbound LAN Focus)

- checked_at_utc: 2026-03-15T19:55:39.4429880Z
- local_url: http://127.0.0.1:18080/
- lan_url: http://192.168.0.27:18080/
- caddy_alive: YES
- listening: 0.0.0.0:18080, [::]:18080

## Checks
- root_access_localhost: YES (200)
- root_access_lan_ip_same_host: YES (200)
- public_repo_state_localhost: YES (200)
- public_repo_state_lan_ip_same_host: YES (200)
- git_path_blocked_local: YES (404)
- env_path_blocked_local: YES (404)
- lan_peer_device_reachability: NO

- status: PASS_LOCAL_BIND_FAIL_PEER_LAN
