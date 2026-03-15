# Public Repo Access Validation

- run_id: public-mirror-validate-20260315T140658Z
- generated_at_utc: 2026-03-15T14:06:58.4015205Z
- updated_at_utc: 2026-03-15T14:11:18.2944209Z
- source_repo_path: E:\CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- public_url: https://e2dd0013569fce.lhr.life
- public_access_mechanism: ssh reverse tunnel via localhost.run
- local_target_url: http://127.0.0.1:18080/
- tunnel_pid: 1872
- tunnel_process_alive: True
- old_broken_public_url: https://074c01864bb287.lhr.life
- old_broken_public_url_cause: stale_tunnel_session_process_not_alive; URL returned 503/no tunnel here
- previous_public_url: https://c115809ee1d89b.lhr.life
- status: PASS

## Checks

- fast_resume_sync: True
```json
{
    "exit_code":  0,
    "output":  [
                   "[public-mirror-fast] source: E:\\CVVCODEX",
                   "[public-mirror-fast] mirror: E:\\_public_repo_mirror\\WorkFLOW",
                   "[public-mirror-fast] engineering_ready: True",
                   "[public-mirror-fast] final_status: PASS",
                   "[public-mirror-fast] progress_json: E:\\CVVCODEX\\setup_reports\\public_mirror_progress_status.json"
               ]
}
```

- required_public_state_files: True
```json
{
    "missing":  [

                ]
}
```

- sync_create_propagation: True
```json
{
    "mirror_probe":  "E:\\_public_repo_mirror\\WorkFLOW\\setup_reports\\.public_mirror_probe_1ad3c00a97ff4fedabf0868d7a637643.txt",
    "sync":  {
                 "exit_code":  0,
                 "output":  [
                                "[public-mirror-fast] source: E:\\CVVCODEX",
                                "[public-mirror-fast] mirror: E:\\_public_repo_mirror\\WorkFLOW",
                                "[public-mirror-fast] engineering_ready: True",
                                "[public-mirror-fast] final_status: PASS",
                                "[public-mirror-fast] progress_json: E:\\CVVCODEX\\setup_reports\\public_mirror_progress_status.json"
                            ]
             },
    "source_probe":  "E:\\CVVCODEX\\setup_reports\\.public_mirror_probe_1ad3c00a97ff4fedabf0868d7a637643.txt"
}
```

- sync_delete_propagation: True
```json
{
    "sync":  {
                 "exit_code":  0,
                 "output":  [
                                "[public-mirror-fast] source: E:\\CVVCODEX",
                                "[public-mirror-fast] mirror: E:\\_public_repo_mirror\\WorkFLOW",
                                "[public-mirror-fast] engineering_ready: True",
                                "[public-mirror-fast] final_status: PASS",
                                "[public-mirror-fast] progress_json: E:\\CVVCODEX\\setup_reports\\public_mirror_progress_status.json"
                            ]
             },
    "mirror_probe_removed":  true
}
```

- sensitive_paths_not_present: True
```json
{
    "leaked_paths":  [

                     ]
}
```

- local_web_access_and_safety: True
```json
{
    "exit_code":  0,
    "output":  [
                   "[public-mirror-web] status=PASS local_url=http://127.0.0.1:18080/",
                   "[public-mirror-web] report_json=E:\\CVVCODEX\\setup_reports\\public_mirror_web_check.json",
                   "[public-mirror-web] report_md=E:\\CVVCODEX\\setup_reports\\public_mirror_web_check.md"
               ]
}
```

- public_url_access_and_safety: True
```json
{
    "exit_code":  0,
    "output":  [
                   "[public-mirror-public] status=PASS public_url=https://e2dd0013569fce.lhr.life",
                   "[public-mirror-public] report_json=E:\\CVVCODEX\\setup_reports\\public_access_check.json",
                   "[public-mirror-public] report_md=E:\\CVVCODEX\\setup_reports\\public_access_check.md"
               ]
}
```
