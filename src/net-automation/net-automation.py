from jinja2 import Template
from netmiko import Netmiko, ConnectHandler
import datetime
import os
import yaml

template_path = "C:\\Users\\Usman\\Desktop\\projects\\network-automation\\src\\net-automation\\j2templates"
vyos_folder = "\\GenVyos"
cisco_folder = "\\GenCisco"

class Main():

    # attributes are standard for netmiko functionality
    def __init__(self, device_type, host, username, password, use_keys, key_file, secret):
        self.device_type = device_type
        self.host = host
        self.username = self.validate_is_string(username)
        self.__password = password
        self.use_keys = self.validate_use_keys(use_keys)
        self.key_file = key_file
        self.secret = self.validate_is_string(secret)

        # netmiko DICTIONARY for network device parameters
        # uses first if statement if the user has a ssh private key file
        # second if using username password auth

        if self.use_keys == True:
            self.data = {
                'device_type': self.device_type,
                'host':   self.host,
                'username': self.username,
                'password': self.__password,
                'key_file': self.key_file,
                'secret': self.secret,
            }
        
        elif self.use_keys == False:
            self.data = {
                'device_type': self.device_type,
                'host':   self.host,
                'username': self.username,
                'password': self.__password,
                'secret': self.secret,
            }

    def init_ssh(self):
        # connects to the device via ssh
        print("Connecting to", self.host, "via SSH")
        self.SSHConnection = ConnectHandler(**self.data)
        print("Connected to", self.host, "via SSH")
    

    def validate_is_string(self, inp):
        if type(inp) != str:
            raise ValueError ("Input is Not String. Check device parameters")
        return inp  # returns inp if the input is valid (string)

    def validate_use_keys(self, inp):
        if type(inp) != bool:
            raise ValueError ("Enter Boolean Value: True or False for use_keys")
        return inp  # returns inp if the input is valid (boolean)
    
    def validate_device_type(self, inp):
        if inp != "cisco_ios" or inp != "ubiquiti_edgerouter" or inp != "vyos":
            raise ValueError ("This framework only supports cisco_ios, vyos, and ubiquti_edgerouter. \n Likely error in device_type.")
        return inp # returns inp if the input is valid (3 specified strings)

    def conv_jinja_to_arr(jinja_output):        # converts string into array of commands (at \n linebreaks)
        array = []                              # creates new array
        for line in jinja_output.splitlines():  # at every line in the split string
            array.append(line)                  # append line to the array
        return (array)                          # return array

    # vendor neutral methods - common commands that are syntaxically identical on various network systems

    def get_data(self):
        return self.data

    def write_file(self, contents, fileName):
        # gets the device type, hostname from self class, and time from get time method 
        fileName += (" " + self.device_type +" " + self.host + " " + (self.get_current_time())+ ".txt")

        file = open((fileName), "w") 
        file.write(contents)

        print ("Wrote File", fileName)
        file.close()

    def get_current_time(self):
        x = datetime.datetime.now()
        return (x.strftime("%H%M %d-%m-%y"))
    
    def custom_command(self, command):
        return (self.SSHConnection.send_command(f"{command}"))

    def get_version(self):
        return (self.SSHConnection.send_command("show version"))

    def run_ping(self, target):
        return (self.SSHConnection.send_command(f"ping {target}"))

    def run_traceroute(self, target):
        print ("Running traceroute to", target)
        return (self.SSHConnection.send_command("traceroute 1.1.1.1"))
    
    def get_route(self, target):
        return (self.SSHConnection.send_command(f"show ip route {target}"))

    def get_bgp_route(self, target):
        return (self.SSHConnection.send_command(f"show ip bgp {target}"))

    def get_route_table(self, modifier):
        return (self.SSHConnection.send_command(f"show ip route {modifier}"))

class Vyos(Main):  # Vyos/EdgeOS specific commands

    # inherits all methods and attributes from the MAIN class
    def __init__(self, host, username, password , use_keys, key_file, secret):
        super().__init__("vyos", host, username, password, use_keys, key_file, secret)
        # calls the __init__ method from the MAIN superclass, creating the netmiko SSH tunnel
    
    def single_command(self, command):
        return (self.SSHConnection.send_command(command))

    def bulk_commands(self, commands):
        self.SSHConnection.config_mode()
        return (self.SSHConnection.send_config_set(commands))

    def config_mode(self):
        self.SSHConnection.config_mode()

    def discard_changes(self):
        return (self.SSHConnection.send_command("discard"))

    def commit(self):
        self.SSHConnection.commit()
        return ("Committed")

    def save_config(self):
        return self.SSHConnection.send_command("save")

    def get_config(self):
        return (self.SSHConnection.send_command('show configuration'))
        
    def get_config_commands(self):
        return (self.SSHConnection.send_command('show configuration commands'))
    
    def get_bgp_neighbors(self):
        return (self.SSHConnection.send_command("show ip bgp summary"))

    def get_interfaces(self):
        return (self.SSHConnection.send_command("show interfaces"))
    
    def get_changed(self):
        return (self.SSHConnection.send_command("compare"))


    # enable interface (delete disable)
    def delete_disable_interface(self, interface_type, interface_name):
        self.SSHConnection.config_mode()
        self.SSHConnection.send_command(f"delete interfaces {interface_type} {interface_name} disable")
    
    def compare(self):
        return self.SSHConnection.send_command("compare")

    ### start of config generation methods

    def gen_hostname(hostname):
        os.chdir(template_path+vyos_folder)                          # navigates to dir containing vyos templates
        with open("gen_hostname.j2") as raw:                         # opens hostname jinja template file
            j2template = raw.read()                                  # reads hostname template file, stores it in j2template var
        output = Template(j2template)                                # associates jinja hostname template with output
        rendered = (output.render(hostname=hostname))                # renders template, with paramater 'hostname', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                    # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_int(conf):
        os.chdir(template_path+vyos_folder)                          # navigates to dir containing vyos templates
        with open("gen_int.j2") as raw:                              # opens interface jinja template file
            j2template = raw.read()                                  # reads interface template file, stores it in j2template var
        output = Template(j2template)                                # associates jinja hostname template with output
        rendered = (output.render(interfaces=conf))                  # renders template, with paramater 'conf', and stores output in 'rendered' var
        return Main.conv_jinja_to_arr(rendered)                      # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_ospf_networks(networks):                      
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open("gen_ospf_network.j2") as raw:                      # opens ospf jinja template file
            j2template = raw.read()                                   # reads ospf template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(networks=networks))                 # renders template, with paramater 'networks', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_bgp_peer(peers, localAS):
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open("gen_bgp_peer.j2") as raw:                          # opens bgp peer jinja template file
            j2template = raw.read()                                   # reads bgp peer template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(peers=peers, localAS=localAS))      # renders template, with paramaters 'peers' & 'localAS', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)
    
    def gen_bgp_prefixes(prefixes, localAS):
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open("gen_bgp_prefixes.j2") as raw:                      # opens bgp prefix jinja template file
            j2template = raw.read()                                   # reads bgp prefix template file, stores it in j2template var
        output = Template(j2template)                                 # closes bgp prefix template file file
        rendered = (output.render(prefixes=prefixes, localAS=localAS))# renders template, with paramater 'prefixes', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)


    def gen_static(static_routes):
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open("gen_static.j2") as raw:                            # opens static jinja template file
            j2template = raw.read()                                   # reads static template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(static=static_routes))              # renders template, with paramater 'static_routes', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)


    def gen_firewalls(firewalls):
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open("gen_firewalls.j2") as raw:                         # opens fw jinja template file
            j2template = raw.read()                                   # reads fw template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(firewalls=firewalls))               # renders template, with paramater 'prefixes', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_dhcp(dhcp):
        os.chdir(template_path+vyos_folder)                           # navigates to dir containing vyos templates
        with open ("gen_dhcp.j2") as raw:                             # opens dhcp jinja template file
            j2template = raw.read()                                   # reads dhcp template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(dhservers=dhcp))                    # renders template, with paramater 'prefixes', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)
    
    def deploy_yaml(ymlfile):

        with open(ymlfile) as file: # opens the yaml file
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

            dhservers = device.get("dhcp")
            if dhservers != None:
                to_deploy.append(Vyos.gen_dhcp(dhservers))

            see_commands = input("Do you want to see the individual commands? Y/N [Y]")
            if see_commands == "N" or  see_commands == "n":  # default is yes
                pass
            
            else:                    # shows commands
                for i in to_deploy:  # loops through command arrays
                    for j in i:
                        print (j)    # and prints them

            deploy = input("Start Deployment? Y/N [Y]")

            if deploy == "N" or deploy == "n": # default is yes
                pass

            else:   # calls Vyos method from OOP, with config from yml file as parms.
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
                    print (Vyos.bulk_commands(router, i))   # send commands over SSH

                verify_commit = input("Do you want to check the command conflicts before comitting? Y//N [Y]") 
                if verify_commit == "N":                                 # asks to check conflicts
                    Vyos.commit(router)                                  # only commits if input is "Y"
                else:                                                    # default input is discard      
                    print (Vyos.get_changed(router))

                commit = input("Do you want to commit Y/N [N]")   # asks to commit
                if commit == "Y":                                 # only commits if input is "Y"
                    Vyos.commit(router)                           # default input is discard      
                else:
                    Vyos.discard_changes(router)

                save = input("Do you want to save the configuration to disk? Y/N [N]")
                if save == "Y" or save == "y":
                    print (Vyos.save_config(router))
                else:
                    print ("Config not saved to disk")



class EdgeOS(Main):  # Vyos/EdgeOS specific commands

    # inherits all methods and attributes from the MAIN class
    def __init__(self, host, username, password , use_keys, key_file, secret):
        super().__init__("ubiquiti_edgerouter", host, username, password, use_keys, key_file, secret)
        # calls the __init__ method from the MAIN superclass, creating the netmiko SSH tunnel

class Cisco_IOS(Main):  # cisco specific commands

    # inherits all methods and attributes from MAIN class
    # sends 'cisco_ios' as an argument, so user doesn't have to specify device_type
    def __init__(self, host, username, password , use_keys, key_file, secret):
        super().__init__("cisco_ios", host, username, password, use_keys, key_file, secret)
        # calls the __init__ function from the MAIN superclass, creating the netmiko SSH tunnel

    def bulk_commands(self, commands):
        self.SSHConnection.enable()
        return (self.SSHConnection.send_config_set(commands))

    # polymorphism - adds .ios
    def write_file(self, contents, fileName):
        # gets the device type, hostname from self class, and time from get time method 
        fileName += (" " + self.device_type +" " + self.host + " " + (self.get_current_time())+ ".ios")

        file = open((fileName), "w") 
        file.write(contents)

        print ("Wrote File", fileName)
        file.close()

    def get_all_config(self):
        self.SSHConnection.enable()
        result = (self.SSHConnection.send_command('show run', use_textfsm=True)) 
        self.SSHConnection.exit_enable_mode()
        return result

    def get_config_include(self, term):
        self.SSHConnection.enable()   # enable cisco enable mode, with self.secret, in superclass 
        result = self.SSHConnection.send_command(f'show run | include {term}', use_textfsm=True)
        self.SSHConnection.exit_enable_mode()
        return result
    
    def get_route_table(self):
        return (self.SSHConnection.send_command("show ip route"))
    
    def get_interfaces_brief(self):
        return (self.SSHConnection.send_command("show ip interface brief", use_textfsm=True))

    def get_route_table(self, modifier):
        return (self.SSHConnection.send_command(f"show ip route {modifier}", use_textfsm=True))

    def get_interfaces(self):
        return (self.SSHConnection.send_command("show ip interface", use_textfsm=True))
    
    def get_arp(self):
        return (self.SSHConnection.send_command("show arp", use_textfsm=True))

    def run_set_interface_desc(self, new_desc):
        pass
        # TODO
    
    ### start of generation methods

    def gen_vlan(vlans):
        os.chdir(template_path+cisco_folder)
        raw = open("gen_vlan.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        rendered = (output.render(vlans=vlans)) 
        return (Main.conv_jinja_to_arr(rendered))                    # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_int(interfaces):
        os.chdir(template_path+cisco_folder)
        raw = open("gen_int.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        rendered = (output.render(interfaces=interfaces)) # left interfaces var in j2 file,
        return (Main.conv_jinja_to_arr(rendered))                    # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_hostname(hostname):
        os.chdir(template_path+cisco_folder)                         # navigates to dir containing vyos templates
        with open("gen_hostname.j2") as raw:                         # opens ospf nets jinja template file
            j2template = raw.read()                                  # reads ospf nets template file, stores it in j2template var
        output = Template(j2template)                                # associates jinja hostname template with output
        rendered = (output.render(hostname=hostname))                # renders template, with paramater 'hostname', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                    # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def gen_ospf_networks(networks):                      
        os.chdir(template_path+cisco_folder)                          # navigates to dir containing vyos templates
        with open("gen_ospf_network.j2") as raw:                      # opens ospf nets jinja template file
            j2template = raw.read()                                   # reads ospf nets template file, stores it in j2template var
        output = Template(j2template)                                 # associates jinja hostname template with output
        rendered = (output.render(networks=networks))                 # renders template, with paramater 'networks', and stores output in 'rendered' var
        return (Main.conv_jinja_to_arr(rendered))                     # pushes rendered var through 'conv_jinja_to_arr' method, to convert commands to an array (needed for netmiko's bulk_commands)

    def deploy_yaml(ymlfile):

        with open(ymlfile) as file: # opens the yaml file
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

            vlans = device.get("vlans")
            if vlans != None:
                to_deploy.append (Cisco_IOS.gen_vlan(vlans))


            see_commands = input("Do you want to see the individual commands? Y/N [Y]")
            if see_commands == "N":  # default is no, due to verbosity of commands
                pass
            else:
                # print (to_deploy)
                for i in to_deploy:  # loops through command arrays
                    for j in i:
                        print (j)    # and prints them


            deploy = input("Start Deployment? Y/N [Y]")

            if deploy == "N":   # calls Vyos method from OOP, with config from yml file as parms.
                pass
            else:
                router1 = Cisco_IOS(
                    device["SSH_conf"]["hostname"],
                    device["SSH_conf"]["username"],
                    device["SSH_conf"]["password"],
                    device["SSH_conf"]["use_keys"],
                    device["SSH_conf"]["key_location"],
                    device["SSH_conf"]["secret"],
                )
                Cisco_IOS.init_ssh(router1)               # starts the SSH connection

                running_conf = Cisco_IOS.get_all_config(router1)

                for command in to_deploy:                       # for every code block generated (every dimension in arr)
                    print (Cisco_IOS.bulk_commands(router1, command))   # send commands over SSH