# Public URL Stability Check

- checked_at_utc: 2026-03-15T18:34:01.1368874Z
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
    "started_at_utc":  "2026-03-15T18:34:19.2577352Z",
    "root_checks_requested":  5,
    "file_rounds_requested":  3,
    "interval_seconds":  4,
    "root_checks":  [
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:34:22.1067644Z",
                            "latency_ms":  2842.44,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  1
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:34:30.9341456Z",
                            "latency_ms":  4788.29,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  2
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:34:37.8053493Z",
                            "latency_ms":  2863.9,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  3
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:34:44.5499616Z",
                            "latency_ms":  2740.14,
                            "url":  "http://185.171.202.83:18080",
                            "attempt":  4
                        },
                        {
                            "ok":  false,
                            "status":  null,
                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                            "checked_at_utc":  "2026-03-15T18:34:52.2005980Z",
                            "latency_ms":  3643.52,
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
                                                            "checked_at_utc":  "2026-03-15T18:34:55.0205861Z",
                                                            "latency_ms":  2815.25,
                                                            "url":  "http://185.171.202.83:18080/PUBLIC_REPO_STATE.json",
                                                            "round":  1,
                                                            "path":  "/PUBLIC_REPO_STATE.json"
                                                        },
                                                        {
                                                            "ok":  false,
                                                            "status":  null,
                                                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                            "checked_at_utc":  "2026-03-15T18:35:08.9620151Z",
                                                            "latency_ms":  2887.22,
                                                            "url":  "http://185.171.202.83:18080/PUBLIC_REPO_STATE.json",
                                                            "round":  2,
                                                            "path":  "/PUBLIC_REPO_STATE.json"
                                                        },
                                                        {
                                                            "ok":  false,
                                                            "status":  null,
                                                            "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                            "checked_at_utc":  "2026-03-15T18:35:23.6032022Z",
                                                            "latency_ms":  2735.19,
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
                                                             "checked_at_utc":  "2026-03-15T18:34:59.1579604Z",
                                                             "latency_ms":  4132.03,
                                                             "url":  "http://185.171.202.83:18080/PUBLIC_SYNC_STATUS.json",
                                                             "round":  1,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json"
                                                         },
                                                         {
                                                             "ok":  false,
                                                             "status":  null,
                                                             "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                             "checked_at_utc":  "2026-03-15T18:35:13.5944632Z",
                                                             "latency_ms":  4631.97,
                                                             "url":  "http://185.171.202.83:18080/PUBLIC_SYNC_STATUS.json",
                                                             "round":  2,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json"
                                                         },
                                                         {
                                                             "ok":  false,
                                                             "status":  null,
                                                             "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                             "checked_at_utc":  "2026-03-15T18:35:26.5988451Z",
                                                             "latency_ms":  2995.17,
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
                                                           "checked_at_utc":  "2026-03-15T18:35:02.0633528Z",
                                                           "latency_ms":  2904.9,
                                                           "url":  "http://185.171.202.83:18080/PUBLIC_ENTRYPOINTS.md",
                                                           "round":  1,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md"
                                                       },
                                                       {
                                                           "ok":  false,
                                                           "status":  null,
                                                           "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                           "checked_at_utc":  "2026-03-15T18:35:16.8591715Z",
                                                           "latency_ms":  3264.15,
                                                           "url":  "http://185.171.202.83:18080/PUBLIC_ENTRYPOINTS.md",
                                                           "round":  2,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md"
                                                       },
                                                       {
                                                           "ok":  false,
                                                           "status":  null,
                                                           "error":  "Базовое соединение закрыто: Соединение было неожиданно закрыто.",
                                                           "checked_at_utc":  "2026-03-15T18:35:29.5458752Z",
                                                           "latency_ms":  2946.57,
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
    "ended_at_utc":  "2026-03-15T18:35:29.5621096Z"
}
```
