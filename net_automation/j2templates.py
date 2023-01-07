vyos_int ="""
{% for int in interfaces -%}

{% if int.state == "absent" -%}
delete interfaces {{ int.type }} {{ int.name }}

{% else %}

{% if int.state == "disabled" -%} 
set interfaces {{ int.type }} {{ int.name }} disable
{%endif-%}

{% if int.state == "present" -%} 
delete interfaces {{ int.type }} {{ int.name }} disable
{%endif-%}

set interfaces {{ int.type }} {{ int.name }} address {{ int.ip }}{{ int.mask }}

{% if int.desc and int.desc|length %}
set interfaces {{ int.type }} {{ int.name }} description '{{ int.desc }}'
{% endif -%}

{% if int.firewall -%}
{% for fw in int.firewall -%}
set interfaces {{ int.type }} {{ int.name }} firewall {{ fw.direction }} name '{{ fw.name }}'
{% endfor -%}
{% endif -%}


{% endif -%}

{% endfor -%}
"""


vyos_wireguard_int ="""
{% if state == "deleted" -%}
delete interfaces {{ type }} {{ name }}

{% else %}

{% if state == "disabled" -%} 
set interfaces {{ type }} {{ name }} disable
{%endif-%}

{% if state == "present" -%} 
delete interfaces {{ type }} {{ name }} disable
{%endif-%}

set interfaces {{ type }} {{ name }} address {{ ip }}{{ mask }}

{% if desc and desc|length %}
set interfaces {{ type }} {{ name }} description '{{ desc }}'
{% endif -%}

{% if firewall -%}
{% for fw in firewall -%}
set interfaces {{ type }} {{ name }} firewall {{ fw.direction }} name '{{ fw.name }}'
{% endfor -%}
{% endif -%}

{%if type == "wireguard" -%}

{% if port is defined and port|length -%}
set interfaces {{ type }} {{ name }} port {{ port }}
{% endif -%}

{% if privkey is defined and privkey|length -%}
set interfaces {{ type }} {{ name }} private-key {{ privkey }}
{% endif -%}

{% for peer in wg_peers -%}

set interfaces {{ type }} {{ name }} peer {{ peer.name }} allowed-ips '{{ peer.allowedips }}'

{% if peer.address is defined and peer.address|length -%}
set interfaces {{ type }} {{ name }} peer {{ peer.name }} address '{{ peer.address }}'
{% endif -%}

{% if peer.port is defined and peer.port|length -%}
set interfaces {{ type }} {{ name }} peer {{ peer.name }} port '{{ peer.port }}'
{% endif -%}

{% if peer.keepalive is defined and peer.keepalive|length -%}
set interfaces {{ type }} {{ name }} peer {{ peer.name }} persistent-keepalive '{{ peer.keepalive }}'
{% endif -%}

set interfaces {{ type }} {{ name }} peer {{ peer.name }} public-key '{{ peer.pubkey }}'

{% endfor -%}

{% endif -%}

{% endif -%}
"""

vyos_bgp_peer = """
{%for peer in peers -%}
{%if peer.state == "absent" -%}
delete protocols bgp {{ localAS }} neighbor {{ peer.ip }}
{% else -%}
{%if peer.state == "disabled"-%}
set protocols bgp {{ localAS }} neighbor {{ peer.ip }} shutdown
{%endif-%}

{% if peer.state == "present" -%}
delete protocols bgp {{ localAS }} neighbor {{ peer.ip }} disable
{% endif -%}

set protocols bgp {{ localAS }} neighbor {{ peer.ip }} remote-as {{ peer.remote_as }}
{%if peer.desc is defined and peer.desc|length -%}
set protocols bgp {{ localAS }} neighbor {{ peer.ip }} description {{ peer.desc }}
{% endif -%}
{%if peer.ebgp_multihop is defined and peer.ebgp_multihop|length -%}
set protocols bgp {{ localAS }} neighbor {{ peer.ip }} ebgp-multihop {{ peer.ebgp_multihop }}
{% endif -%}
{%if peer.route_maps -%}
{%for rm in peer.route_maps -%}  
{%if rm.state == "absent" -%}
delete protocols bgp {{ localAS }} neighbor {{ peer.ip }} address-family ipv4-unicast route-map {{ rm.action }} {{ rm.route_map }}
{% else -%}
set protocols bgp {{ localAS }} neighbor {{ peer.ip }} address-family ipv4-unicast route-map {{ rm.action }} {{ rm.route_map }}
{%endif -%}
{%endfor -%}
{%endif -%} 
{%endif -%}
{% endfor -%}"""


vyos_ospf = """
{% if ospf["ospf_redistribute"] is defined %}

{% for redis in ospf["ospf_redistribute"] %}

{% if redis.state == "present" %}
set protocols ospf redistribute {{ redis.redistribute }}

{% if redis.route_map is defined and redis.route_map|length > 1 %}
set protocols ospf redistribute {{ redis.redistribute }} route-map {{ redis.route_map }}
{% endif %}

{% elif redis.state == "absent"%}
delete protocol ospf redistribute {{ redis.redistribute }}
{% endif %}

{% endfor %}

{% endif %}

{% if ospf["ospf_parameters"]["use_routerid"] == True and ospf["ospf_parameters"]["routerid"] is defined and ospf["ospf_parameters"]["routerid"]| length %}
set protocols ospf parameters router-id {{ ospf["ospf_parameters"]["routerid"] }}
{% endif %}

{% if ospf["ospf_parameters"]["use_routerid"] == False %}
delete protocols ospf area 0 parameters router-id
{% endif %}

{% for net in ospf["ospf_networks"] -%}

{% if net.state == "absent" -%}
delete protocols ospf area {{ net.area }} network {{ net.subnet }}{{ net.mask }}

{% else -%}
set protocols ospf area {{ net.area }} network {{ net.subnet }}{{ net.mask }} 

{% endif -%}

{% endfor -%}"""                                   


vyos_bgp_prefixes = """
{% for prefix in prefixes -%}
{% if prefix.state == "absent" -%}
delete protocols bgp {{ localAS }} address-family {{ prefix.address_family }} network {{ prefix.prefix }}{{ prefix.mask }}
{% else -%}
set protocols bgp {{ localAS }} address-family {{ prefix.address_family }} network {{ prefix.prefix }}{{ prefix.mask }}
{% endif -%}
{% endfor -%}"""


vyos_routemap = """
{%- for map in route_maps -%}

{%if map.desc is defined and map.desc|length -%}
set policy route-map {{ map.name }} description '{{map.desc}}'
{%endif-%}

{%- for rule in map.rules -%}

{%if rule.state == "absent" -%}
delete policy route-map {{ map.name }} rule {{ rule.rule_no }}

{% else -%}
set policy route-map {{ map.name }} rule {{ rule.rule_no }} action {{ rule.action }}
set policy route-map {{ map.name }} rule {{ rule.rule_no }} match {{ rule.match }}
{%endif-%}
{% endfor -%}{% endfor -%}"""


vyos_prefix_list = """
{%- for list in prefix_lists -%}

{%if list.desc is defined and list.desc|length -%}
set policy prefix-list {{ list.name }} description '{{ list.desc }}'
{%endif-%}

{%- for rule in list.rules -%}

{%if rule.state == "absent" -%}
delete policy prefix-list {{ list.name }} rule {{ rule.rule_no }}

{% else -%}
set policy prefix-list {{ list.name }} rule {{ rule.rule_no }} action {{ rule.action }}
set policy prefix-list {{ list.name }} rule {{ rule.rule_no }} {{ rule.match[0]["length"] }}
set policy prefix-list {{ list.name }} rule {{ rule.rule_no }} prefix {{ rule.match[0]["prefix"] }}
{%endif-%}
{% endfor -%}{% endfor -%}"""


vyos_static = """
{% for route in static -%}
{% if route.state == "absent" -%}
delete protocols static {{ route.type }} {{ route.network }}
{% else -%}
set protocols static {{ route.type }} {{ route.network }} next-hop-interface {{ route.nexthop }}
{% if route.distance is defined and route.distance|length -%}
set protocols static {{ route.type }} {{ route.network }} next-hop-interface {{ route.nexthop }} distance {{ route.distance }}
{%endif -%}
{%endif -%}

{% if route.type == "route" -%}
set protocols static {{ route.type }} {{ route.network }} next-hop {{ route.nexthop }}

{% if route.distance is defined and route.distance|length -%}
set protocols static {{ route.type }} {{ route.network }} next-hop {{ route.nexthop }} distance {{ route.distance }}
{%endif -%}
{%endif -%}

{%endfor -%}"""

vyos_firewall  = """
{% for ruleset in firewalls -%}

set firewall name {{ ruleset.name }} 
set firewall name {{ ruleset.name }} default-action '{{ ruleset.default_action }}'

{% for rule in ruleset.rules -%}

{% if rule.state == "absent" -%}
delete firewall name {{ ruleset.name }} rule {{ rule.rule_no }}
{% else -%}

set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} action '{{ rule.action }}'

{% if rule.desc is defined and rule.desc|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} description '{{ rule.desc }}' 
{%endif -%}

{% if rule.dest is defined -%}

{% for d in rule.dest -%}

{% if d["address"] is defined and d["address"]|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} destination address "{{ d['address'] }}"
{% endif -%}

{% if d['port'] is defined and d['port']|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} destination port "{{ d['port'] }}"
{% endif -%}

{% if d['group'] is defined and d['group']|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} destination group {{ d['group'] }}
{% endif -%}

{% endfor-%}

{% endif -%}


{% if rule.source is defined and rule.source|length -%}

{% for s in rule.source -%}

{% if s["address"] is defined and s["address"]|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} source address "{{ s['address'] }}"
{% endif -%}

{% if s["port"] is defined and s["port"]|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} source port "{{ s['port'] }}"
{% endif -%}

{% endfor-%}

{%endif -%}

{% if rule.protocol is defined and rule.protocol|length -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} protocol '{{ rule.protocol }}' 
{%endif -%}


{% if rule.states is defined -%}

{% for state in rule.states -%}
{% if state.status == "absent" -%}
delete firewall name {{ ruleset.name }} rule {{ rule.rule_no }} state {{ state.name }} enable
{% else -%}
set firewall name {{ ruleset.name }} rule {{ rule.rule_no }} state {{ state.name }} enable
{% endif -%}
{% endfor -%}

{% endif -%}
{% endif -%}

{% endfor -%}

{%endfor -%}"""

vyos_zones = """
{% for zone in zones -%}

{% if zone.state == "deleted" -%}
delete zone-policy zone "{{ zone.name }}"
{% else -%}

{% if zone.state == "replaced" -%}
delete zone-policy zone "{{ zone.name }}"
{% endif -%}

set zone-policy zone "{{ zone.name }}"
set zone-policy zone "{{ zone.name }}" default-action "{{ zone.default_action }}"

{% if zone.desc is defined and zone.desc | length -%}
set zone-policy zone "{{ zone.name }}" description '{{ zone.desc }}"
{% endif -%}

{% for flow in zone.flows -%}
set zone-policy zone "{{ zone.name }}" from "{{ flow.from }}" firewall name "{{ flow.firewall }}"
{% endfor -%}

{% for int in zone.interfaces %}
set zone-policy zone "{{ zone.name }}" interface "{{ int }}"
{% endfor -%}


{% endif -%}


{% endfor -%}
"""

vyos_dhcp = """
{% for dhserver in dhservers -%}

{% if dhserver.subnet is defined and dhserver.subnet|length -%}
{% if dhserver.default_router is defined and dhserver.default_router|length %}
set service dhcp-server shared-network-name {{ dhserver.name }} subnet  {{ dhserver.subnet }}
set service dhcp-server shared-network-name {{dhserver.name}} subnet  {{ dhserver.subnet }} default-router {{ dhserver.default_router }}
{%endif -%}
{%endif -%}

{% if dhserver.domain_name is defined and dhserver.domain_name|length -%}
set service dhcp-server shared-network-name {{ dhserver.name }} domain-name {{ dhserver.doman_name }}
{% endif -%}

{% if dhserver.name_server is defined and dhserver.name_server|length -%}
set service dhcp-server shared-network-name {{ dhserver.name }} subnet {{ dhserver.subnet }} name-server {{ dhserver.name_server}}
{% endif -%}

{% if dhserver.lease_time is defined and dhserver.lease_time|length -%}
set service dhcp-server shared-network-name {{ dhserver.name }} subnet {{ dhserver.subnet }} lease {{ dhserver.lease_time }}
{% endif -%}

{% if dhserver.authoritative == "true" -%}
set service dhcp-server shared-network-name {{ dhserver.name }} authoritative
{% endif -%}

{% if dhserver.exclude_addrs is defined and dhserver.exclude_addrs -%}
{% for addr in dhserver.exclude_addrs -%}
set service dhcp-server shared-network-name {{dhserver.name}} subnet {{dhserver.subnet}} exclude {{ addr.ip }}
{% endfor -%}
{% endif -%}


{%if dhserver.dhcp_reserv is defined and dhserver.dhcp_reserv -%}
{%for reserv in dhserver.dhcp_reserv -%}
set service dhcp-server shared-network-name {{dhserver.name}} subnet {{dhserver.subnet}} static-mapping {{reserv.desc}} mac-address {{ reserv.mac }}
set service dhcp-server shared-network-name {{dhserver.name}} subnet {{dhserver.subnet}} static-mapping {{reserv.desc}} ip-address {{reserv.ip}}
{%endfor -%}
{%endif -%}

{%endfor -%}"""


vyos_lldp = """
{% if interfaces is defined and interfaces|length -%}

{% for interface in interfaces -%}
set service lldp interface {{ interface }}
{% endfor -%}

{% endif -%}

{% if legacy_protocols is defined and legacy_protocols|length -%}

{% for protocol in legacy_protocols -%}
set service lldp legacy-protocols {{ protocol }}
{% endfor -%}
{% endif -%}"""

edgeos_int  ="""
{% for int in interfaces -%}

{% if int.state == "absent" -%}
delete interfaces {{ int.type }} {{ int.name }}

{% else %}

{% if int.state == "disabled" -%} 

set interfaces {{ int.type }} {{ int.name }} disable
{% endif -%}
set interfaces {{ int.type }} {{ int.name }} address {{ int.ip }}{{ int.mask }}

{% if int.desc and int.desc|length %}
set interfaces {{ int.type }} {{ int.name }} description '{{ int.desc }}'
{% endif -%}

{% if int.firewall -%}
{% for fw in int.firewall -%}
set interfaces {{ int.type }} {{ int.name }} firewall {{ fw.direction }} name '{{ fw.name }}'
{% endfor -%}
{% endif -%}

{% if int.vifs is defined and int.vifs|length -%}
{% for vif in int.vifs -%}

{% if vif.state == "disabled" -%}
set interfaces {{ int.type }} {{ int.name }} vif {{ vif.number }} disable
{% endif -%}

{% if vif.state == "absent" -%}
delete interfaces {{ int.type }} {{ int.name }} vif {{ vif.number }}
{% endif -%}

set interfaces {{ int.type }} {{ int.name }} vif {{ vif.number }} address {{ vif.ip }}{{ vif.mask }}
set interfaces {{ int.type }} {{ int.name }} vif {{ vif.number }} description '{{ vif.desc }}'

{% endfor %}

{% endif -%}

{%if int.type == "wireguard" -%}
{% if int.port is defined and int.port|length -%}
set interfaces {{ int.type }} {{ int.name }} listen-port {{ int.port }}
{% endif -%}

{% for peer in int.wg_peers -%}

set interfaces {{ int.type }} {{ int.name }} peer {{ peer.pubkey }} allowed-ips '{{ peer.allowedips }}'

{% if peer.endpoint is defined and peer.endpoint|length -%}
set interfaces {{ int.type }} {{ int.name }} peer {{ peer.pubkey }} endpoint '{{ peer.endpoint }}'
{% endif -%}

{% if peer.name is defined and peer.name|length -%}
set interfaces {{ int.type }} {{ int.name }} peer {{ peer.pubkey }} description '{{ peer.name }}'
{% endif %}

{% if peer.keepalive is defined and peer.keepalive|length -%}
set interfaces {{ int.type }} {{ int.name }} peer {{ peer.pubkey }} persistent-keepalive '{{ peer.keepalive }}'
{% endif -%}

{% endfor -%}

{% if int.private_key_path is defined and int.private_key_path|length -%}
set interfaces {{ int.type }} {{ int.name }} private-key '{{ int.private_key_path }}'
{% endif %}

{% if int.route_allowed_ips is defined and int.route_allowed_ips|length -%}
set interfaces {{ int.type }} {{ int.name }} route-allowed-ips '{{ int.route_allowed_ips }}'
{% endif %}

{% endif -%}

{% endif -%}

{% endfor -%}
"""

edgeos_lldp = """
{% if interfaces is defined and interfaces|length -%}

{% for interface in interfaces -%}
set service lldp interface {{ interface }}

{% endfor -%}
{% endif -%}

{% if legacy_protocols is defined and legacy_protocols|length -%}

{% for protocol in legacy_protocols -%}
set service lldp legacy-protocols {{ protocol }}
{% endfor -%}
{% endif -%}"""


ios_vlan = """
{% for vlan in vlans -%}}

vlan {{ vlan.id }}
  name {{ desc }}
{% if vlan.state == "disabled" -%}
  shutdown
{% endif -%}
{% endfor -%}}"""

ios_int = """
{% for int in interfaces -%}

{% if int.state == 'absent' -%}
interface {{ int.name }}
shutdown
{% endif -%}
interface {{ int.name }}
description {{ int.desc }}
{% if int.routed == True -%}
no switchport
ip address {{int.ip}} {{int.mask}}
{% endif -%}


{% if int.mode == "trunk" -%}
switchport mode trunk
{% endif -%}

{% if int.native_vlan is defined and int.native_vlan|length -%}
switchport trunk native vlan {{ int.native_vlan}}
{% endif -%}

{% if int.spanning_tree == "portfast trunk" -%}
spanning-tree portfast trunk
{% endif -%}

{% if int.allowed_vlans is defined and int.allowed_vlans|length -%}
switchport trunk allowed vlan {{ int.allowed_vlans }}
{% endif -%}

{% if int.access_vlan is defined and int.access_vlan|length -%}
switchport access vlan {{ int.access_vlan }}
{% endif -%}

{% if int.mode == "access" -%}
switchport mode access
{% endif -%}

{% if int.spanning_tree == "portfast" -%}
spanning-tree portfast
{% endif -%}


no shutdown

{% endfor %}
"""

ios_ospf = """
router ospf 1

{% for net in networks %}

{% if net.state == "absent" -%}
 no network {{ net.subnet }} {{ net.mask }} area {{ net.area }}
{% else -%}
 network {{ net.subnet }} {{ net.mask }} area {{ net.area }}{% endif -%}
{% endfor -%}
"""

ios_lldp = """
{% if run == true %}
cdp run
{% elif run == false %}
no cdp run
{% endif %}"""