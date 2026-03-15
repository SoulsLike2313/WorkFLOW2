# Public URL Stability Check

- checked_at_utc: 2026-03-15T18:06:53.5511490Z
- public_access_provider: direct_local_pc_caddy
- public_access_mechanism: direct local-PC hosting via Caddy (non-tunnel canonical)
- session_based_url: False
- final_public_url: http://185.171.202.83:18080
- classification: BROKEN
- stable_enough_for_chatgpt: False
- repeated_checks_passed: 0/14
- failed_checks: 14

## Full Series JSON
```json
{
    "enabled":  true,
    "started_at_utc":  "2026-03-15T18:07:11.7836960Z",
    "root_checks_requested":  5,
    "file_rounds_requested":  3,
    "interval_seconds":  4,
    "root_checks":  [
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:07:14.5694724Z",
                            "latency_ms":  2778.83,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  1
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:07:22.5127535Z",
                            "latency_ms":  3908.59,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  2
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:07:30.3600691Z",
                            "latency_ms":  3832.43,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  3
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:07:37.3104322Z",
                            "latency_ms":  2942.96,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  4
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:07:44.3199113Z",
                            "latency_ms":  2999.76,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  5
                        }
                    ],
    "file_checks":  {
                        "/PUBLIC_REPO_STATE.json":  [
                                                        {
                                                            "ok":  false,
                                                            "status":  null,
                                                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                            "checked_at_utc":  "2026-03-15T18:07:47.1599443Z",
                                                            "latency_ms":  2834.97,
                                                            "url":  "http://185.171.202.83:18080/PUBLIC_REPO_STATE.json",
                                                            "round":  1,
                                                            "path":  "/PUBLIC_REPO_STATE.json"
                                                        },
                                                        {
                                                            "ok":  false,
                                                            "status":  null,
                                                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                            "checked_at_utc":  "2026-03-15T18:07:59.6041521Z",
                                                            "latency_ms":  2921.34,
                                                            "url":  "http://185.171.202.83:18080/PUBLIC_REPO_STATE.json",
                                                            "round":  2,
                                                            "path":  "/PUBLIC_REPO_STATE.json"
                                                        },
                                                        {
                                                            "ok":  false,
                                                            "status":  null,
                                                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                            "checked_at_utc":  "2026-03-15T18:08:12.1455676Z",
                                                            "latency_ms":  2732.95,
                                                            "url":  "http://185.171.202.83:18080/PUBLIC_REPO_STATE.json",
                                                            "round":  3,
                                                            "path":  "/PUBLIC_REPO_STATE.json"
                                                        }
                                                    ],
                        "/PUBLIC_SYNC_STATUS.json":  [
                                                         {
                                                             "ok":  false,
                                                             "status":  null,
                                                             "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                             "checked_at_utc":  "2026-03-15T18:07:49.8530403Z",
                                                             "latency_ms":  2687.58,
                                                             "url":  "http://185.171.202.83:18080/PUBLIC_SYNC_STATUS.json",
                                                             "round":  1,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json"
                                                         },
                                                         {
                                                             "ok":  false,
                                                             "status":  null,
                                                             "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                             "checked_at_utc":  "2026-03-15T18:08:02.3273531Z",
                                                             "latency_ms":  2722.81,
                                                             "url":  "http://185.171.202.83:18080/PUBLIC_SYNC_STATUS.json",
                                                             "round":  2,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json"
                                                         },
                                                         {
                                                             "ok":  false,
                                                             "status":  null,
                                                             "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                             "checked_at_utc":  "2026-03-15T18:08:14.8909406Z",
                                                             "latency_ms":  2744.91,
                                                             "url":  "http://185.171.202.83:18080/PUBLIC_SYNC_STATUS.json",
                                                             "round":  3,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json"
                                                         }
                                                     ],
                        "/PUBLIC_ENTRYPOINTS.md":  [
                                                       {
                                                           "ok":  false,
                                                           "status":  null,
                                                           "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                           "checked_at_utc":  "2026-03-15T18:07:52.6675250Z",
                                                           "latency_ms":  2814.1,
                                                           "url":  "http://185.171.202.83:18080/PUBLIC_ENTRYPOINTS.md",
                                                           "round":  1,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md"
                                                       },
                                                       {
                                                           "ok":  false,
                                                           "status":  null,
                                                           "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                           "checked_at_utc":  "2026-03-15T18:08:05.4052951Z",
                                                           "latency_ms":  3077.42,
                                                           "url":  "http://185.171.202.83:18080/PUBLIC_ENTRYPOINTS.md",
                                                           "round":  2,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md"
                                                       },
                                                       {
                                                           "ok":  false,
                                                           "status":  null,
                                                           "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                           "checked_at_utc":  "2026-03-15T18:08:29.7245602Z",
                                                           "latency_ms":  14833.11,
                                                           "url":  "http://185.171.202.83:18080/PUBLIC_ENTRYPOINTS.md",
                                                           "round":  3,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md"
                                                       }
                                                   ]
                    },
    "successful_checks":  0,
    "failed_checks":  14,
    "total_checks":  14,
    "success_rate_percent":  0,
    "classification":  "BROKEN",
    "stable_enough_for_chatgpt":  false,
    "session_based_url":  false,
    "ended_at_utc":  "2026-03-15T18:08:29.7408539Z"
}
```
