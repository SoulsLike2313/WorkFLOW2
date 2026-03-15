# Final Operator WAN Focus Update

- updated_at_utc: 2026-03-15T20:47:37.0507272Z
- canonical_mechanism: direct local-PC hosting via Caddy
- source_path: E:\CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- local_web_url: http://127.0.0.1:18080/
- public_target_url: http://185.171.202.83:18080/
- LAN reachability: CONFIRMED
- WAN reachability: FAIL
- exact_break_point: WAN-side path (router WAN forwarding effectiveness / ISP ingress policy). Host/LAN stack is not the break point.
- CGNAT/double NAT suspected: NO
- ISP inbound block suspected: YES
- one_exact_next_step: Verify WAN-interface binding (ppp0) for TCP 18080 forward to 192.168.0.27:18080 and retest from off-LAN.
