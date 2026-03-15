# Public Repo Access Validation

- run_id: public-mirror-validate-20260315T173540Z
- generated_at_utc: 2026-03-15T17:35:40.7513903Z
- source_repo_path: E:\CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- public_url: 
- status: FAIL

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
    "mirror_probe":  "E:\\_public_repo_mirror\\WorkFLOW\\setup_reports\\.public_mirror_probe_2d753424759a483ba825eaa32d143b6c.txt",
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
    "source_probe":  "E:\\CVVCODEX\\setup_reports\\.public_mirror_probe_2d753424759a483ba825eaa32d143b6c.txt"
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

- public_url_access_and_safety: False
```json
{
    "reason":  "public_url_not_available"
}
```
