# Direct Public Access Validation (Packet Path Verdict)

- generated_at_utc: 2026-03-15T20:28:13.2371576Z
- mode: PACKET_PATH_VERDICT_ONLY_NO_REBUILD
- packet_capture_run: YES
- capture_tool: pktmon
- capture_filter: TCP SYN port 18080
- capture_file: E:\CVVCODEX\setup_reports\pktmon_test.etl
- capture_text: E:\CVVCODEX\setup_reports\pktmon_test.txt

## Packet facts
- SYN from LAN client reached host: NO
- host response (SYN-ACK/HTTP) observed: NO
- explicit reset/drop packet observed: NO_EXPLICIT_PACKET_EVENT
- trigger from LAN client confirmed in capture window: UNKNOWN

## Exact verdict
- PATH_BROKEN_BEFORE_HOST_OR_TRIGGER_NOT_SENT

## Exact break point
- No inbound SYN to 192.168.0.27:18080 observed on host capture window; break is before host stack (router bridge/AP isolation/segmentation) unless LAN client request was not sent during capture window.

## One exact next step
- Run one synchronized test: start capture, then immediately execute on LAN laptop:
  curl http://192.168.0.27:18080/PUBLIC_REPO_STATE.json
  and report exact timestamp of execution.

- Caddy/mirror/sync/NAT were not changed in this run.
