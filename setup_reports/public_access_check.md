# Public Access Check

- checked_at_utc: 2026-03-15T11:36:31.5608735Z
- public_url: https://6ae9b5512f6b67.lhr.life
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
