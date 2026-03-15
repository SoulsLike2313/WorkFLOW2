# Public URL Stability Check

- checked_at_utc: 2026-03-15T15:27:56.6840463Z
- source_repo_path: E:\CVVCODEX
- public_access_provider: ssh_localhost_run
- public_access_mechanism: ssh reverse tunnel via localhost.run (bound to non-VPN interface)
- session_based_url: True
- final_public_url: https://10df7336ba08d7.lhr.life
- classification: SESSION_FRAGILE
- stable_enough_for_chatgpt: False
- repeated_checks_passed: 14/14
- failed_checks: 0
- url_changes_detected: 0
- had_tunnel_drop: False

## Full Series JSON
```json
{
    "enabled":  true,
    "started_at_utc":  "2026-03-15T15:28:05.7186919Z",
    "root_checks_requested":  5,
    "file_rounds_requested":  3,
    "interval_seconds":  8,
    "session_based_url":  true,
    "root_checks":  [
                        {
                            "checked_at_utc":  "2026-03-15T15:28:07.2245485Z",
                            "ok":  true,
                            "status":  200,
                            "latency_ms":  1483.4,
                            "error":  null,
                            "attempt":  1,
                            "url":  "https://10df7336ba08d7.lhr.life",
                            "tunnel_process_alive":  true
                        },
                        {
                            "checked_at_utc":  "2026-03-15T15:28:16.6100409Z",
                            "ok":  true,
                            "status":  200,
                            "latency_ms":  1351.3,
                            "error":  null,
                            "attempt":  2,
                            "url":  "https://10df7336ba08d7.lhr.life",
                            "tunnel_process_alive":  true
                        },
                        {
                            "checked_at_utc":  "2026-03-15T15:28:26.2030793Z",
                            "ok":  true,
                            "status":  200,
                            "latency_ms":  1557.09,
                            "error":  null,
                            "attempt":  3,
                            "url":  "https://10df7336ba08d7.lhr.life",
                            "tunnel_process_alive":  true
                        },
                        {
                            "checked_at_utc":  "2026-03-15T15:28:35.5906738Z",
                            "ok":  true,
                            "status":  200,
                            "latency_ms":  1379.36,
                            "error":  null,
                            "attempt":  4,
                            "url":  "https://10df7336ba08d7.lhr.life",
                            "tunnel_process_alive":  true
                        },
                        {
                            "checked_at_utc":  "2026-03-15T15:28:44.7317211Z",
                            "ok":  true,
                            "status":  200,
                            "latency_ms":  1130.48,
                            "error":  null,
                            "attempt":  5,
                            "url":  "https://10df7336ba08d7.lhr.life",
                            "tunnel_process_alive":  true
                        }
                    ],
    "file_checks":  {
                        "/PUBLIC_REPO_STATE.json":  [
                                                        {
                                                            "checked_at_utc":  "2026-03-15T15:28:46.1879237Z",
                                                            "ok":  true,
                                                            "status":  200,
                                                            "latency_ms":  1445.92,
                                                            "error":  null,
                                                            "round":  1,
                                                            "path":  "/PUBLIC_REPO_STATE.json",
                                                            "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_REPO_STATE.json",
                                                            "tunnel_process_alive":  true
                                                        },
                                                        {
                                                            "checked_at_utc":  "2026-03-15T15:29:12.1894437Z",
                                                            "ok":  true,
                                                            "status":  200,
                                                            "latency_ms":  13940.08,
                                                            "error":  null,
                                                            "round":  2,
                                                            "path":  "/PUBLIC_REPO_STATE.json",
                                                            "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_REPO_STATE.json",
                                                            "tunnel_process_alive":  true
                                                        },
                                                        {
                                                            "checked_at_utc":  "2026-03-15T15:29:24.4167432Z",
                                                            "ok":  true,
                                                            "status":  200,
                                                            "latency_ms":  1548.95,
                                                            "error":  null,
                                                            "round":  3,
                                                            "path":  "/PUBLIC_REPO_STATE.json",
                                                            "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_REPO_STATE.json",
                                                            "tunnel_process_alive":  true
                                                        }
                                                    ],
                        "/PUBLIC_SYNC_STATUS.json":  [
                                                         {
                                                             "checked_at_utc":  "2026-03-15T15:28:48.8334355Z",
                                                             "ok":  true,
                                                             "status":  200,
                                                             "latency_ms":  2632.83,
                                                             "error":  null,
                                                             "round":  1,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json",
                                                             "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_SYNC_STATUS.json",
                                                             "tunnel_process_alive":  true
                                                         },
                                                         {
                                                             "checked_at_utc":  "2026-03-15T15:29:13.6851850Z",
                                                             "ok":  true,
                                                             "status":  200,
                                                             "latency_ms":  1488.2,
                                                             "error":  null,
                                                             "round":  2,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json",
                                                             "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_SYNC_STATUS.json",
                                                             "tunnel_process_alive":  true
                                                         },
                                                         {
                                                             "checked_at_utc":  "2026-03-15T15:29:26.3028322Z",
                                                             "ok":  true,
                                                             "status":  200,
                                                             "latency_ms":  1879.81,
                                                             "error":  null,
                                                             "round":  3,
                                                             "path":  "/PUBLIC_SYNC_STATUS.json",
                                                             "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_SYNC_STATUS.json",
                                                             "tunnel_process_alive":  true
                                                         }
                                                     ],
                        "/PUBLIC_ENTRYPOINTS.md":  [
                                                       {
                                                           "checked_at_utc":  "2026-03-15T15:28:50.2373202Z",
                                                           "ok":  true,
                                                           "status":  200,
                                                           "latency_ms":  1395.62,
                                                           "error":  null,
                                                           "round":  1,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md",
                                                           "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_ENTRYPOINTS.md",
                                                           "tunnel_process_alive":  true
                                                       },
                                                       {
                                                           "checked_at_utc":  "2026-03-15T15:29:14.8505201Z",
                                                           "ok":  true,
                                                           "status":  200,
                                                           "latency_ms":  1157.88,
                                                           "error":  null,
                                                           "round":  2,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md",
                                                           "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_ENTRYPOINTS.md",
                                                           "tunnel_process_alive":  true
                                                       },
                                                       {
                                                           "checked_at_utc":  "2026-03-15T15:29:28.5238112Z",
                                                           "ok":  true,
                                                           "status":  200,
                                                           "latency_ms":  2213.92,
                                                           "error":  null,
                                                           "round":  3,
                                                           "path":  "/PUBLIC_ENTRYPOINTS.md",
                                                           "url":  "https://10df7336ba08d7.lhr.life/PUBLIC_ENTRYPOINTS.md",
                                                           "tunnel_process_alive":  true
                                                       }
                                                   ]
                    },
    "tunnel_process_alive_sequence":  [
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:05.7333775Z",
                                              "phase":  "root",
                                              "attempt":  1,
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:15.2582211Z",
                                              "phase":  "root",
                                              "attempt":  2,
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:24.6452087Z",
                                              "phase":  "root",
                                              "attempt":  3,
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:34.2112346Z",
                                              "phase":  "root",
                                              "attempt":  4,
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:43.6007901Z",
                                              "phase":  "root",
                                              "attempt":  5,
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:44.7403206Z",
                                              "phase":  "file",
                                              "round":  1,
                                              "path":  "/PUBLIC_REPO_STATE.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:46.2000090Z",
                                              "phase":  "file",
                                              "round":  1,
                                              "path":  "/PUBLIC_SYNC_STATUS.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:48.8410507Z",
                                              "phase":  "file",
                                              "round":  1,
                                              "path":  "/PUBLIC_ENTRYPOINTS.md",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:28:58.2480928Z",
                                              "phase":  "file",
                                              "round":  2,
                                              "path":  "/PUBLIC_REPO_STATE.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:29:12.1965369Z",
                                              "phase":  "file",
                                              "round":  2,
                                              "path":  "/PUBLIC_SYNC_STATUS.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:29:13.6923024Z",
                                              "phase":  "file",
                                              "round":  2,
                                              "path":  "/PUBLIC_ENTRYPOINTS.md",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:29:22.8672679Z",
                                              "phase":  "file",
                                              "round":  3,
                                              "path":  "/PUBLIC_REPO_STATE.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:29:24.4228621Z",
                                              "phase":  "file",
                                              "round":  3,
                                              "path":  "/PUBLIC_SYNC_STATUS.json",
                                              "tunnel_process_alive":  true
                                          },
                                          {
                                              "checked_at_utc":  "2026-03-15T15:29:26.3095173Z",
                                              "phase":  "file",
                                              "round":  3,
                                              "path":  "/PUBLIC_ENTRYPOINTS.md",
                                              "tunnel_process_alive":  true
                                          }
                                      ],
    "url_changes_detected":  [

                             ],
    "latest_url":  "https://10df7336ba08d7.lhr.life",
    "successful_checks":  14,
    "failed_checks":  0,
    "total_checks":  14,
    "success_rate_percent":  100,
    "had_tunnel_drop":  false,
    "classification":  "SESSION_FRAGILE",
    "stable_enough_for_chatgpt":  false,
    "ended_at_utc":  "2026-03-15T15:29:28.5421832Z"
}
```
