# Direct Public Network Diagnosis

- generated_at_utc: 2026-03-15T18:13:22.7436851Z
- active_interface: Ethernet
- lan_ip: 192.168.0.27
- gateway: 192.168.0.1
- gateway_reachable: True
- external_ip: 185.171.202.83
- nat_situation: private_lan_with_nat
- cgnat_or_double_nat: not_confirmed_from_local_only
- router_http_reachable: True
- router_http_status: 200
- upnp_available: False
- upnp_reason: static_mapping_collection_unavailable
- firewall_rule_for_18080: True
- canyouseeme_checked: True
- canyouseeme_result_line: <p style="padding-left:15px"><font color="red"><b>Error:</b></font>&nbsp;I could <b>not</b> see your service on <b>185.171.202.83</b> on port (<b>18080</b>)<br>Reason:<small>&nbsp;Connection timed out</small></p>

## Listening Ports (80/443/18080)
```json
{
    "local_address":  "::",
    "local_port":  18080,
    "pid":  11012,
    "process":  "caddy"
}
```
