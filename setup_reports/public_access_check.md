# Public Access Check

- checked_at_utc: 2026-03-15T16:33:47.1683322Z
- public_url: https://9b8191c9412744.lhr.life
- public_access_provider: ssh_localhost_run
- public_access_mechanism: ssh reverse tunnel via localhost.run (bound to non-VPN interface)
- public_access_vpn_dependent: False
- local_target_url: http://127.0.0.1:18080/
- tunnel_pid: 1168
- tunnel_process_alive: True
- old_public_url: https://787e4105496bcf.lhr.life
- old_broken_public_url: https://0e6748b97ae3fe.lhr.life
- old_broken_public_url_cause: stale_session_hostname_not_mapped
- latest_tunnel_url_from_logs: https://9b8191c9412744.lhr.life
- runtime_url_outdated: True
- session_based_url: True
- stability_classification: SESSION_FRAGILE
- stable_enough_for_chatgpt: False
- repeated_checks_passed: 25/25
- failure_cause: 
- status: PASS

## Checks

- root_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- state_file_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- sync_status_file_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- entrypoints_file_access
```json
{
    "ok":  true,
    "status":  200,
    "error":  null
}
```

- git_path_blocked
```json
{
    "pass":  true,
    "probe":  {
                  "ok":  false,
                  "status":  404,
                  "error":  "Удаленный сервер возвратил ошибку: (404) Не найден."
              }
}
```

- env_path_blocked
```json
{
    "pass":  true,
    "probe":  {
                  "ok":  false,
                  "status":  404,
                  "error":  "Удаленный сервер возвратил ошибку: (404) Не найден."
              }
}
```

- vpn_independent
```json
{
    "pass":  true,
    "value":  true
}
```
