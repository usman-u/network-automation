from Netmiko_OOP import *
import yaml

with open("routers.yml") as file:
    raw = yaml.safe_load(file)

for device in raw["routers"]:
    print ("----", device["name"],"----")

    print (Vyos.gen_int(device["interfaces"]))
    print (Vyos.gen_bgp_peer(device["bgp_peers"], device["bgpasn"]))
    print (Vyos.gen_ospf_networks(device["ospf_networks"]))