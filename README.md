# Network Automation

An *Ansible like* Network Automation Framework, Using Python OOP and Netmiko to interface with Cisco IOS, VyOS, EdgeOS network devices.

# Developer Notes
```bash
conda create -n network-automation
create activate network-automation
poetry install
```
If using VSCode SSH remote, change interpreter to conda env python path.

e.g. `/home/usman/miniconda3/envs/network-automation/bin/python`

Confirm with `which python`
```
(network-automation) usman@dev-usman-lan:~/network-automation$ which python
/home/usman/miniconda3/envs/network-automation/bin/python
```
# Usage

## Example 1: Getting Basic Device Information from a VyOS Router 
Importing the class from the package.
```py
from net_automation import net_automation
```
Creating an instance of the VyOS class, with specified parameters.
```py
router_1 = net_automation.Vyos(
    "router-1.com",                                                      # Hostname/IP
    "username",                                                          # Username
    "",                                                                  # Password   
    True,                                                                # Boolean switch for using SSH Keys. (password not needed if True)
    "/home/user/.ssh/id_rsa",                                            # SSH Key file location
    "")                                                                  # Secret (left empty, as Cisco Only)
```
Establishing the SSH connection to "router_1" and getting interfaces.
```py
router_1.init_ssh()                                                      # Creates the SSH connection to the VyOS router

print (router_1.get_interfaces())                                        # Returns Interfaces from the VyOS router

Codes: S - State, L - Link, u - Up, D - Down, A - Admin Down
Interface        IP Address                        S/L  Description
---------        ----------                        ---  -----------
eth0             a.b.c.d/23                        u/u  WAN 
lo               127.0.0.1/8                       u/u  dn42-vyos 
                 10.100.100.4/32
                 ::1/128
wg12             172.22.132.170/30                 u/u  p2p_usman 

```
Getting a traceroute to "8.8.8.8".
```py
print (router_1.get_route("8.8.8.8"))                                   # Returns traceroute to specific IP

traceroute to 8.8.8.8 (8.8.8.8), 30 hops max, 60 byte packets
 1  vlan32.core01.lil01.fr.virtua.systems (185.154.155.1)  0.633 ms  0.483 ms  0.350 ms
 2  po31.core02.lil01.fr.virtua.systems (188.214.24.177)  0.266 ms  0.125 ms  0.145 ms
 3  188.214.24.20 4.866 ms  4.867 ms  4.848 ms
 4  google1.par.franceix.net (37.49.237.172)  8.769 ms  9.160 ms  8.835 ms
 5  108.170.244.161 9.585 ms 108.170.244.225 9.982 ms 108.170.244.161 9.647 ms
 6  216.239.48.43 8.850 ms 142.250.224.197 15.357 ms 216.239.48.45 9.662 ms
 7  dns.google (8.8.8.8)  9.607 ms  8.734 ms  9.453 ms
```
Storing returned route table and configuration in variables.
```
configuration = (router_1.get_config())                                
route_table = (router_1.get_route_table())
```

---

## Example 2: Generating and Deploying Configurations to a VyOS Router.
### .py file
```py
from net_automation import net_automation

net_automation.Vyos.deploy_yaml("router.yml")
```
Executing the Python script should generate and deploy configs, based on the contents of the YAML file. 
### `router.yml` file
```yaml
routers:
  - name: "vyos-dn42-01"
    SSH_conf:
      hostname: "10.0.0.1"
      username: "username"
      password: ""
      use_keys: True
      key_location: "C:\\Users\\user\\.ssh\\id_rsa"
      secret: ""
    
    firewalls:
      - name: "WAN_Local"
        state: "present"
        default_action: "drop"
        rules:
          - rule_no: "10"
            state: "present"
            action: "accept"
            desc: "accept SSH"
            dest: "port 22"
            source: ""
            protocol: "tcp_udp"

          - rule_no: "30"
            state: "present"
            action: "accept"
            desc: "accept wg 51890"
            dest: "port 51890"
            source: ""
            protocol: "udp"

          - rule_no: "90"
            state: "present"
            action: "accept"
            desc: "allow estab related traffic"
            states:
              - name: "established"
                status: "present"
              - name: "related"
                status: "enabled"

    interfaces:
      - name: "eth0"
        type: "ethernet"
        state: "present"
        ip: "dhcp"
        mask: ""
        desc: "WAN"

      - name: "lo"
        type: "loopback"
        state: "present"
        ip: "10.100.100.4"
        mask: "/32"
        desc: ""

    static:
      - type: "interface-route"
        network: "172.20.16.141/32"
        nexthop: "wg15"
        distance: ""
        state: "present"

    bgpasn: "4242421869"
    bgp_prefixes:
      - prefix: "172.22.132.160"
        mask: "/27"
        address_family: "ipv4-unicast"
        state: "present"

    bgp_peers:
      - ip: "172.20.53.104"
        state: "present"
        remote_as: "4242423914"
        ebgp_multihop: "255"
        desc: "kioubit"

        route_maps:
          - route_map: "DN42-ROA"
            action: "import"
            state: "present"
          - route_map: "DN42-ROA"
            action: "export"
            state: "present"
```

## Example 3: Backing up device configurations.
Creating instances CiscoIOS and EdgeOS classes, for Cisco switches and Ubiquiti switches.
```py
cisco_2960 = net_automation.Cisco_IOS(
    "cisco-2960.lan",
    "usman",
    "password", 
    False, 
    "", 
    "ciscosecret")

cisco_3560 = net_automation.Cisco_IOS(
    "cisco-3560.lan",
    "username",
    "password", 
    False, 
    "", 
    "ciscosecret")

ubiquiti_erx = net_automation.EdgeOS(
    "ubiquiti-erx.lan", 
    "username", 
    "", 
    True, 
    r"C:\Users\Usman\.ssh\id_rsa", 
    "")

ubiquiti_er4 = net_automation.EdgeOS(
    "ubiquit-er4.lan", 
    "usman", 
    "", 
    True, 
    r"C:\Users\Usman\.ssh\id_rsa", 
    "")
```
For loops that get device configurations and writes them to external files.
```py
cisco_switches = [cisco_2960, cisco_3560]

for device in cisco_switches:                                                               # iterates through the "cisco_switches" array and:
    to_write = Cisco_IOS.get_all_config(device)                                             # stores the outputs from method in the "to_write" variable
    Cisco_IOS.write_file(device, to_write, "")                                              # writes the output to new files                            
```

```py
ubiquti_routers = [ubiquiti_erx, ubiquiti_er4]

for device in ubiquti_routers:                                                              # iterates through the "ubiquiti_routers" array and:
    to_write = Vyos.get_config(device)                                                      # stores the outputs from method in the "to_write" variable
    Main.write_file(device, to_write, "")                                                   # writes the output to new files                            
```
