# Direct Public Access Validation (Packet Capture Verdict)

- generated_at_utc: 2026-03-15T20:45:35.1995200Z
- packet_capture_run: YES
- tool: pktmon
- etl: E:\CVVCODEX\setup_reports\pktmon_test.etl
- txt: E:\CVVCODEX\setup_reports\pktmon_test.txt
- filter: TCP SYN, IP 192.168.0.27, port 18080

## Packet Facts
- SYN observed: YES
- SYN flow: 192.168.0.1:60182 -> 192.168.0.27:18080 (Flags [S])
- host response observed: YES (component counters show Rx=1 and Tx=1 during matched flow)

## Exact Verdict
- HOST_STACK_RESPONDS; BREAK_IS_UPSTREAM_OF_HOST_FOR_CLIENT_PATH

## Exact Break Point
- Wi-Fi client path segmentation / AP isolation / router bridge policy between LAN laptop and Ethernet host.

## One Exact Next Step
- Disable AP/client isolation on the active Wi-Fi SSID and retest from laptop:
  curl http://192.168.0.27:18080/PUBLIC_REPO_STATE.json

- Caddy/mirror/sync/NAT/VPN config were not changed in this packet-capture run.
