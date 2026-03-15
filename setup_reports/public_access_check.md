# Public Access Check

- checked_at_utc: 2026-03-15T12:06:38.3829388Z
- public_url: https://074c01864bb287.lhr.life
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
