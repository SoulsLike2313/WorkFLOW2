# Server Sync Current State

- checked_at_utc: 2026-03-15T11:59:02.4299395Z
- source_repo_path: E:/CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- branch: main
- head_commit: eaef89d44cc3f4783d23288b28442743e6c55e05
- git_status_clean: False
- git_status_changed_count: 17
- source_files: 35327
- source_directories: 3046
- source_size_bytes: 3828835174
- mirror_files: 35306
- mirror_directories: 3046
- mirror_size_bytes: 3827381934
- active_sync_entrypoint: tools/public_mirror/fast_resume_public_mirror.ps1
- fast_resume_entrypoint: tools/public_mirror/fast_resume_public_mirror.ps1
- manual_sync_entrypoint: tools/public_mirror/sync_repo_to_public_mirror.ps1

## Relevant Processes

```json
[
    {
        "ProcessId":  16868,
        "Name":  "python.exe",
        "CommandLine":  "\"C:\\Users\\PC\\AppData\\Local\\Programs\\Python\\Python312\\python.exe\" -m http.server 18080 --bind 127.0.0.1 --directory E:\\_public_repo_mirror\\WorkFLOW "
    },
    {
        "ProcessId":  1844,
        "Name":  "ssh.exe",
        "CommandLine":  "\"C:\\Windows\\System32\\OpenSSH\\ssh.exe\" -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=accept-new -R 80:127.0.0.1:18080 nokey@localhost.run "
    }
]
```
