# Public Access Check (WAN-Side Only)

- generated_at_utc: 2026-03-15T21:09:47.3663138Z
- LAN reachability: CONFIRMED
- WAN reachability: FAIL

## Result
- External URL check failed for: http://185.171.202.83:18080/PUBLIC_REPO_STATE.json
- Local/LAN path remains healthy and is not the blocker.

## Exact break point
- WAN ingress/forwarding effectiveness on active WAN path (router/ISP side).

## One exact next step
- Bind TCP 18080 forward to active WAN interface (ppp0) -> 192.168.0.27:18080 and retest from off-LAN.
