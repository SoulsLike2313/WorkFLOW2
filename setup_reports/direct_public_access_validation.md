# Direct Public Access Validation (Factual Dry Check)

- generated_at_utc: 2026-03-15T19:39:44.7535722Z
- check_mode: FACTUAL_DRY_CHECK_ONLY
- chain: Internet -> router NAT/port forwarding -> 192.168.0.27:18080 -> Caddy -> E:\_public_repo_mirror\WorkFLOW

## Stage 1 - Local Base
- Caddy process alive: YES (PID 11012)
- local port 18080 listening: YES
- http://127.0.0.1:18080/: YES (200)
- /PUBLIC_REPO_STATE.json local: YES (200)
- /.git/ local blocked: YES (404)
- /.env local blocked: YES (404)

## Stage 2 - Windows Firewall
- inbound TCP 18080 block present: NO
- inbound TCP 18080 allow present: YES (WorkFLOW Public Mirror Caddy 18080)
- firewall fix required: NO

## Stage 3 - Router/NAT Side
- expected router rule: TCP 18080 -> 192.168.0.27:18080
- router NAT rule confirmed from inside: UNKNOWN
- NAT loopback may distort same-network verification: YES

## Stage 4 - Public Reachability
- http://185.171.202.83:18080/: FAIL (connection closed)
- /PUBLIC_REPO_STATE.json: FAIL (connection closed)
- /PUBLIC_SYNC_STATUS.json: FAIL (connection closed)
- /PUBLIC_ENTRYPOINTS.md: FAIL (connection closed)
- verdict: INDETERMINATE

## Stage 5 - Exact Break Point
- NAT loopback prevents reliable in-network verification of external endpoint; router NAT rule presence is not confirmed from inside LAN.

## One Exact Next Step
- Run one off-LAN check (mobile network) for http://185.171.202.83:18080/PUBLIC_REPO_STATE.json to confirm real external reachability.
