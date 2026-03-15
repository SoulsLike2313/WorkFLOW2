# Public Access Check

- checked_at_utc: 2026-03-15T14:13:18.4977410Z
- public_url: https://e2dd0013569fce.lhr.life
- public_access_mechanism: ssh reverse tunnel via localhost.run
- local_target_url: http://127.0.0.1:18080/
- tunnel_pid: 1872
- tunnel_process_alive: True
- old_public_url: https://c115809ee1d89b.lhr.life
- old_broken_public_url: https://074c01864bb287.lhr.life
- old_broken_public_url_cause: stale_tunnel_session_process_not_alive; URL returned 503/no tunnel here
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
