# WAN Path Validation (Canonical WAN-Side Focus)

- generated_at_utc: 2026-03-15T21:09:47.3663138Z
- LAN reachability: CONFIRMED
- WAN reachability: FAIL

## Canonical state
- localhost/LAN/Caddy/internal stack: NOT THE BLOCKER
- public target: http://185.171.202.83:18080/

## WAN-side classification
- router NAT/port forwarding effective on WAN side: NO (suspected ineffective)
- wrong WAN interface binding (ppp0 path mismatch): YES (suspected)
- ISP inbound filtering/policy block: YES (suspected)
- CGNAT/double NAT: NO (not primary signal)

## Exact WAN-side break point
- WAN ingress path does not reliably hit effective forwarding to 192.168.0.27:18080 on active WAN route; host/LAN stack is confirmed healthy.

## One exact next step
- On router WAN/NAT page, explicitly bind TCP 18080 forwarding to active WAN interface (ppp0) -> 192.168.0.27:18080, then immediately retest from off-LAN mobile network.
