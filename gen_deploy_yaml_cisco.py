from Netmiko_OOP import *
import yaml
from netmiko import Netmiko, ConnectHandler

with open("ent_routers.yaml") as file: # opens the yaml file
    raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var
    
for device in raw["routers"]:
    print ("----", device["name"],"----")

    to_deploy = []

    hostname = device.get("name")               
    if hostname != None:                                 # if key exists in yaml file
        to_deploy.append (Cisco_IOS.gen_hostname(hostname))         # generate command and append to array

    interfaces = device.get("interfaces")
    if interfaces != None:
        to_deploy.append (Cisco_IOS.gen_int(interfaces))

    bgpasn = device.get("bgpasn")
    bgp_peers = device.get("bgp_peers")

    if bgpasn != None and bgp_peers != None:
        to_deploy.append (Cisco_IOS.gen_bgp_peer(bgp_peers, bgpasn))
    
    bgp_prefixes = device.get("bgp_prefixes")
    if bgp_prefixes != None:
        to_deploy.append (Cisco_IOS.gen_bgp_prefixes(bgp_prefixes))

    ospf_networks = device.get("ospf_networks")
    if ospf_networks != None:
        to_deploy.append (Cisco_IOS.gen_ospf_networks(ospf_networks))

    print (to_deploy)

    # deploy = input("\nRead modifications; Y to deploy; N to discard")

    # if deploy == "Y":   # calls Cisco_IOS method from OOP, with config from yml file as parms.
    router1 = Cisco_IOS(
        device["SSH_conf"]["hostname"],
        device["SSH_conf"]["username"],
        device["SSH_conf"]["password"],
        device["SSH_conf"]["use_keys"],
        device["SSH_conf"]["key_location"],
        device["SSH_conf"]["secret"],
    )
    Cisco_IOS.init_ssh(router1)               # starts the SSH connection
    for command in to_deploy:                       # for every code block generated (every dimension in arr)
        Cisco_IOS.bulk_commands(router1, command)   # send commands over SSH