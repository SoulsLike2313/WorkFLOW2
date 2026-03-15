# Final Operator Report

- generated_at_utc: 2026-03-15T14:23:41.9090333Z
- architecture: local source repo -> external mirror -> local web server -> public tunnel URL
- github_is_not_source_of_truth: True
- source_repo_path: E:\CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- source_branch: main
- source_head_commit: 0e1c2a0f4c469b90620c51305c67196fdd9c186c
- local_url: http://127.0.0.1:18080/
- public_url: https://ac85f2bd6236a2.lhr.life
- public_access_mechanism: ssh reverse tunnel via localhost.run
- public_url_runtime_status: READY
- public_url_runtime_blocker: 
- tunnel_pid: 1872
- local_server_pid: 14280
- old_broken_public_url: https://074c01864bb287.lhr.life
- old_broken_public_url_cause: stale_tunnel_session_process_not_alive; URL returned 503/no tunnel here
- previous_public_url: https://e2dd0013569fce.lhr.life
- latest_tunnel_url_from_logs: https://ac85f2bd6236a2.lhr.life
- runtime_url_outdated: False
- engineering_ready: True
- current_stage: COMPLETE_FAST_MODE
- excludes_file: setup_reports/public_mirror_excludes.txt

## Entrypoints
- fast_resume: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/fast_resume_public_mirror.ps1 -SourceRepoPath E:\CVVCODEX -MirrorPath E:\_public_repo_mirror\WorkFLOW -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt -StageATimeBudgetSeconds 180 -StageBTimeBudgetSeconds 180
- resume: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/resume_public_mirror.ps1 -SourceRepoPath E:\CVVCODEX
- manual_sync: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/sync_repo_to_public_mirror.ps1 -SourceRepoPath E:\CVVCODEX -MirrorPath E:\_public_repo_mirror\WorkFLOW -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
- watch: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/start_public_mirror_watch.ps1 -SourceRepoPath E:\CVVCODEX -MirrorPath E:\_public_repo_mirror\WorkFLOW -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
- web_start: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/start_public_mirror_web.ps1 -SourceRepoPath E:\CVVCODEX -MirrorPath E:\_public_repo_mirror\WorkFLOW
- web_stop: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/stop_public_mirror_web.ps1 -SourceRepoPath E:\CVVCODEX
- web_check: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/check_public_mirror_web.ps1 -SourceRepoPath E:\CVVCODEX
- public_access_start: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/start_public_mirror_public_access.ps1 -SourceRepoPath E:\CVVCODEX -Port 18080
- public_access_check: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/check_public_mirror_public_access.ps1 -SourceRepoPath E:\CVVCODEX
- validate: powershell -NoProfile -ExecutionPolicy Bypass -File tools/public_mirror/validate_public_mirror.ps1 -SourceRepoPath E:\CVVCODEX -MirrorPath E:\_public_repo_mirror\WorkFLOW -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt

## Engineering Ready Definition
- README/docs/workspace_config/scripts/projects are available in mirror
- PUBLIC_REPO_STATE.* + PUBLIC_SYNC_STATUS.* + PUBLIC_ENTRYPOINTS.md exist in mirror
- sensitive paths (.git/.env/keys/tokens/secrets) are excluded
- create/delete propagation check passes

## Heavy Tail Deferred
- runtime
- setup_assets
