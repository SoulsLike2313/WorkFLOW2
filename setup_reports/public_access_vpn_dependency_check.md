# Public Access VPN Dependency Check

- generated_at_utc: 2026-03-15T14:31:57.1486660Z
- source_repo_path: E:/CVVCODEX
- mirror_path: E:\_public_repo_mirror\WorkFLOW
- current_public_access_mechanism: ssh reverse tunnel via localhost.run
- mechanism_command: ssh -R 80:127.0.0.1:18080 nokey@localhost.run
- local_target_url: http://127.0.0.1:18080/
- current_public_url: https://ac85f2bd6236a2.lhr.life
- local_web_ok: True
- current_public_url_ok: True
- vpn_dependency_assessment: POTENTIAL_DEPENDENCY_PRESENT

## Findings
- Public access uses session-based ssh reverse tunnel (localhost.run).
- Default route includes tunnel interface (happ-tun) in current state.
- Session-based hostname can become stale (previous no tunnel/503 incidents).

## Passive Network Signals
```json
{
    "vpn_like_interfaces":  [
                                {
                                    "Name":  "happ-tun",
                                    "InterfaceDescription":  "sing-tun Tunnel",
                                    "Status":  "Up",
                                    "LinkSpeed":  "100 Gbps"
                                }
                            ],
    "default_routes":  [
                           {
                               "DestinationPrefix":  "0.0.0.0/0",
                               "NextHop":  "172.18.0.2",
                               "RouteMetric":  0,
                               "InterfaceAlias":  "happ-tun",
                               "ifIndex":  10
                           },
                           {
                               "DestinationPrefix":  "0.0.0.0/0",
                               "NextHop":  "192.168.0.1",
                               "RouteMetric":  0,
                               "InterfaceAlias":  "Ethernet",
                               "ifIndex":  2
                           }
                       ],
    "potential_route_dependency":  true
}
```

## Tunnel Process
```json
{
    "ProcessId":  1872,
    "Name":  "ssh.exe",
    "CommandLine":  "\"C:\\Windows\\System32\\OpenSSH\\ssh.exe\" -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=accept-new -R 80:127.0.0.1:18080 nokey@localhost.run "
}
```
