# Server Sync Current State

- checked_at_utc: 2026-03-15T12:09:37.8405901Z
- source_repo_path: E:/CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- branch: main
- head_commit: 0e1c2a0f4c469b90620c51305c67196fdd9c186c
- git_status_clean: False
- git_status_changed_count: 15
- source_files: 35327
- source_directories: 3046
- source_size_bytes: 3828839980
- mirror_files: 35306
- mirror_directories: 3046
- mirror_size_bytes: 3827383670
- active_sync_entrypoint: tools/public_mirror/fast_resume_public_mirror.ps1
- fast_resume_entrypoint: tools/public_mirror/fast_resume_public_mirror.ps1
- manual_sync_entrypoint: tools/public_mirror/sync_repo_to_public_mirror.ps1

## Relevant Processes

```json
[
    {
        "ProcessId":  11452,
        "Name":  "python.exe",
        "CommandLine":  "\"C:\\Users\\PC\\AppData\\Local\\Programs\\Python\\Python312\\python.exe\" -m http.server 18080 --bind 127.0.0.1 --directory E:\\_public_repo_mirror\\WorkFLOW "
    },
    {
        "ProcessId":  7212,
        "Name":  "ssh.exe",
        "CommandLine":  "\"C:\\Windows\\System32\\OpenSSH\\ssh.exe\" -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=accept-new -R 80:127.0.0.1:18080 nokey@localhost.run "
    }
]
```
