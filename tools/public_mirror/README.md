# Public Mirror Toolkit

## Canonical Model

- source of truth: local repo (`E:\CVVCODEX`)
- public vitrine: sanitized mirror (`E:\_public_repo_mirror\WorkFLOW`)
- canonical local hosting: **Caddy direct local-PC hosting**
- canonical public strategy: direct inbound access to local PC (router/NAT/DDNS/domain path)
- tunnels (`localhost.run`, quick tunnels, ngrok session endpoints) are **legacy fallback only**, not canonical
- `github_is_not_source_of_truth = true`
- canonical local bind: `0.0.0.0:18080`
- canonical local read URL: `http://127.0.0.1:18080/`

## Fast Sync (Unchanged)

- recommended entrypoint:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\fast_resume_public_mirror.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -ExcludesFilePath E:\CVVCODEX\setup_reports\public_mirror_excludes.txt
```

- additional entrypoints (unchanged):
  - `resume_public_mirror.ps1`
  - `sync_repo_to_public_mirror.ps1`
  - `start_public_mirror_watch.ps1`
  - `validate_public_mirror.ps1`

Caddy does not run sync. Caddy only serves the existing mirror.

## Canonical Web Operations

- start canonical local web (Caddy):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\start_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -MirrorPath E:\_public_repo_mirror\WorkFLOW `
  -BindAddress 0.0.0.0 `
  -Port 18080
```

- stop canonical local web:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\stop_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

- check canonical local web:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\check_public_mirror_web.ps1 `
  -SourceRepoPath E:\CVVCODEX
```

## Canonical Public Access Readiness (Direct Hosting)

- initialize direct-hosting runtime (non-tunnel):
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\start_public_mirror_public_access.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -CanonicalHostname "<your-ddns-or-domain-or-public-ip>" `
  -PublicScheme http `
  -PublicPort 18080
```

- check public access and stability:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\public_mirror\check_public_mirror_public_access.ps1 `
  -SourceRepoPath E:\CVVCODEX `
  -RunStabilitySeries `
  -RootCheckCount 10 `
  -FileCheckRounds 5 `
  -IntervalSeconds 6
```

## Caddy Config

- canonical config path: `tools/public_mirror/Caddyfile`
- mirror is served with directory browsing
- sensitive paths are denied/hidden:
  - `.git*`, `.env*`
  - `*.pem`, `*.key`, `*.pfx`, `*.p12`
  - `id_rsa*`, `id_ed25519*`
- `secrets.*`, `token*`, `credentials*`

## Router/NAT Canonical Mapping

- external port: `18080/TCP`
- internal host: `192.168.0.27`
- internal port: `18080`
- service target: Caddy mirror server

Single manual step if external URL is not ready:
- create router port-forward rule `TCP 18080 -> 192.168.0.27:18080`

Current DDNS/domain state:
- no DDNS credential/config in repo/env
- fallback public target is external IP literal (`http://<external_ip>:18080`)

## ENGINEERING READY

Mirror is engineering-ready when:
- mirror is available via canonical local URL
- `PUBLIC_REPO_STATE.json`, `PUBLIC_SYNC_STATUS.json`, `PUBLIC_ENTRYPOINTS.md` are reachable
- sensitive paths are blocked

PC powered on = link works.  
PC powered off = link unavailable (expected for direct local-PC hosting).
