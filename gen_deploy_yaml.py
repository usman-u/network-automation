from Netmiko_OOP import *
import yaml

with open("dn42.yml") as file: # opens the yaml file
    raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var
    
for device in raw["routers"]:
    print ("----", device["name"],"----")

    to_deploy = []

    hostname = device.get("name")               
    if hostname != None:                                 # if key exists in yaml file
        to_deploy.append (Vyos.gen_hostname(hostname))         # generate command and append to array

    interfaces = device.get("interfaces")
    if interfaces != None:
        to_deploy.append (Vyos.gen_int(interfaces))

    bgpasn = device.get("bgpasn")
    bgp_peers = device.get("bgp_peers")

    if bgpasn != None and bgp_peers != None:
        to_deploy.append (Vyos.gen_bgp_peer(bgp_peers, bgpasn))
    
    bgp_prefixes = device.get("bgp_prefixes")
    if bgp_prefixes != None:
        to_deploy.append (Vyos.gen_bgp_prefixes(bgp_prefixes, bgpasn))

    ospf_networks = device.get("ospf_networks")
    if ospf_networks != None:
        to_deploy.append (Vyos.gen_ospf_networks(ospf_networks))
    
    firewalls = device.get("firewalls")
    if firewalls != None:
        to_deploy.append(Vyos.gen_firewalls(firewalls))

    static_routes = device.get("static")
    if static_routes != None:
        to_deploy.append(Vyos.gen_static(static_routes))

    see_commands = input("Do you want to see the individual commands? Y/N [Y]")
    if see_commands == "N":  # default is no, due to verbosity of commands
        pass
    else:
        for i in to_deploy:  # loops through command arrays
            for j in i:
                print (j)    # and prints them

    deploy = input("Start Deployment? Y/N [Y]")

    if deploy == "Y":   # calls Vyos method from OOP, with config from yml file as parms.
        router = Vyos(
            device["SSH_conf"]["hostname"],
            device["SSH_conf"]["username"],
            device["SSH_conf"]["password"],
            device["SSH_conf"]["use_keys"],
            device["SSH_conf"]["key_location"],
            device["SSH_conf"]["secret"],
        )
        Vyos.init_ssh(router)               # starts the SSH connection
        Vyos.config_mode(router)            # enters Vyos config mode
        for i in to_deploy:                 # for every code block generated (every 1st dimension in arr)
            Vyos.bulk_commands(router, i)   # send commands over SSH

        verify_commit = input("Do you want to check the command conflicts before comitting? Y//N [Y]") 
        if verify_commit == "N":
            Vyos.commit(router)                 # send the commit command to the Vyos router
        else:
            print (Vyos.get_changed(router))
        commit = input("Do you want to commit Y/N [N]")
        if commit == "N":
            Vyos.discard_changes(router)
        else:
            Vyos.commit(router)

        save = input("Do you want to save the configuration to disk? Y/N [N]")
        if save == "Y" or save == "y":
            print (Vyos.save_config(router))
        else:
            print ("Config not saved to disk")