from Netmiko_OOP import *
import yaml

with open("routers.yml") as file:
    raw = yaml.safe_load(file)

for device in raw["routers"]:
    print ("----", device["name"],"----")
    # print (GenVyos.gen_int(device["interfaces"]))
    # print (GenVyos.gen_bgp_peer(device["bgp_peers"], device["bgpasn"]))

    print (GenVyos.gen_ospf_networks(device["ospf_networks"]))