# WAN Path Validation (After LAN Confirmed)

- generated_at_utc: 2026-03-15T20:47:37.0507272Z
- LAN reachability: CONFIRMED
- WAN reachability: FAIL

## Confirmed facts
- Caddy alive: YES
- LAN bind/listen path: OK
- inbound LAN path to 192.168.0.27:18080: OK
- Windows firewall as break point: NO
- off-LAN access to http://185.171.202.83:18080/: FAIL

## WAN-side signs
- port-forward effective on WAN side: NO
- wrong WAN interface binding possible (ppp0 mismatch): YES
- ISP inbound block suspected: YES
- CGNAT/double NAT suspected: NO

## Exact break point
- WAN-side path (router WAN forwarding effectiveness / ISP ingress policy). Host/LAN stack is not the break point.

## One exact next step
- In router admin, verify that TCP 18080 forward is bound to active WAN interface (ppp0) and points to 192.168.0.27:18080, then retest from off-LAN mobile network.
