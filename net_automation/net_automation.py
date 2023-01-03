from jinja2 import Template
from netmiko import Netmiko, ConnectHandler
from net_automation import j2templates
import datetime
import os
import yaml
import pySMTP
import re
import matplotlib.pyplot as plt
from discord_webhook import DiscordWebhook
from difflib import Differ
import requests
import textfsm

class Main():

    # attributes are standard for netmiko functionality
    def __init__(self, **kwargs):

        # gets ssh data from kwargs object
        self.device_type = kwargs.get("device_type")
        self.host = kwargs.get("host")
        self.nickname = kwargs.get("nickname")
        self.username = self.validate_is_string(kwargs.get("username"))
        self.__password = kwargs.get("password")
        self.use_keys = self.validate_use_keys(kwargs.get("use_keys"))
        self.key_file = kwargs.get("key_file")
        self.secret = kwargs.get("secret")

        # SSH dict for netmiko
        self.SSH_data = {
            'device_type': self.device_type,
            'host':   self.host,
            'username': self.username,
            'password': self.__password,
            'key_file': self.key_file,
            'secret': self.secret,
        }

    def init_ssh(self):
        # connects to the device via ssh
        print ("Connecting to", self.host)
        self.SSHConnection = ConnectHandler(**self.SSH_data)
        print ("Connected to", self.host)
    
    def validate_is_string(self, inp):
        if type(inp) != str:
            raise ValueError ("Input is Not String. Check device parameters")
        return inp  # returns inp if the input is valid (string)

    def validate_use_keys(self, inp):
        # if type(inp) != bool:
        #     raise ValueError ("Enter Boolean Value: True or False for use_keys")
        return inp  # returns inp if the input is valid (boolean)
    
    def validate_device_type(self, inp):
        if inp != "cisco_ios" or inp != "ubiquiti_edgerouter" or inp != "vyos":
            raise ValueError ("This framework only supports cisco_ios, vyos, and ubiquti_edgerouter. \n Likely error in device_type.")
        return inp # returns inp if the input is valid (3 specified strings)

    def conv_jinja_to_arr(jinja_output):        # converts string into array of commands (at \n linebreaks)
        array = []                              # creates new array
        for line in jinja_output.splitlines():  # at every line in the split string
            array.append(line)                  # append line to the array
        return (list(filter(None, array)))      # uses filter to strip out empty strings from the array 

    def _unidiff_output(expected, actual):
        """
        Helper function. Returns a string containing the unified diff of two multiline strings.
        """

        import difflib
        expected=expected.splitlines(1)
        actual=actual.splitlines(1)

        diff=difflib.unified_diff(expected, actual)

        return ''.join(diff)


    # vendor neutral methods - common commands that are syntaxically identical on various network systems

    def get_data(self):
        return self.data
    
    def get_hostname(self):
        return self.host

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

    # MATPLOTLIB METHODS

    # gets ping data to a host, from a router and returns a plot-able array 
    def get_ping_data(self, target, requests):
        x = []
        y = []
        for i in range (0, requests):
            raw = (self.run_ping(target, 1))

            # regex to specific find the ping data (target, packet loss, min, avg, max, std_dev) and put into groups
            results = re.findall(r"^PING\b[^(]*\(([^)]*)\)\s([^.]*)\..*?^(\d+\sbytes).*?icmp_seq=(\d+).*?ttl=(\d+).*?time=(.*?ms).*?(\d+)\spackets\stransmitted.*?(\d+)\sreceived.*?(\d+%)\spacket\sloss.*?time\s(\d+ms).*?=\s([^\/]*)\/([^\/]*)\/([^\/]*)\/(.*?)\sms", raw, re.MULTILINE|re.DOTALL)
            print ("Ping :", results[0][11], "ms")
            x.append (int(i))
            y.append (float(results[0][11]))

        title = ("Ping to {} ({}) on {}".format(results[0][0],target,(self.host)))
        xlabel = "ICMP Packets Transmitted"
        ylabel = "Ping Time (ms)"
        
        return x, y

    def gen_ping_graph(ping_data):


        plt.plot (ping_data[0],   # x axis
                    ping_data[1], # y axis
                    marker='o', color='red', label='Ping')
        plt.xlabel(ping_data[2])
        plt.ylabel(ping_data[3])
        plt.title(ping_data[4])
        return plt.show()

class Email():
    def __init__(self, sender_email, sender_password):
        self.sender_email=self.verify_email(sender_email)
        self.sender_password=sender_password

    def verify_email(self, email):
        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.fullmatch (regex, email):
            return email
        else:
            raise ValueError("Incorrect Email Formatting, tested via Regex")
    
    def send(self, receiver_email, email_subject, email_body):
        self.receiver_email=self.verify_email(receiver_email)
        self.email_subject=email_subject
        self.email_body=email_body
        pySMTP.send_email(
            self.sender_email, self.sender_password, self.receiver_email, self.email_subject, self.email_body)

class Webhook():
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send(self, content):

        webhook = DiscordWebhook(url=self.webhook_url, content=content, username="NET",  rate_limit_retry=True)
        webhook.execute()

class Vyos(Main):  # Vyos/EdgeOS specific commands
    """
    Functions specific to VyOS
    """

    # inherits all methods and attributes from the MAIN class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
    
    def whois_dn42(self, query):
        return self.SSHConnection.send_command("whois -h whois.dn42 {}" .format(query))

    def save_config(self):
        return self.SSHConnection.send_command("save")

    def get_config(self):
        return (self.SSHConnection.send_command('show configuration'))
        
    def get_config_commands(self):
        return (self.SSHConnection.send_command('show configuration commands'))
    
    def get_ospf_route_all(self):
        return (self.SSHConnection.send_command('show ip ospf route'))
    
    def get_ospf_neighbors(self):
        return (self.SSHConnection.send_command("show ip ospf neighbor"))

    def get_bgp_summary(self):
        raw = (self.SSHConnection.send_command("show ip bgp summary"))

        with open('vyosbgp.template') as template:
            fsm = textfsm.TextFSM(template)
            result = fsm.ParseText(raw)
        
        return result

    def get_interfaces(self):
        """Gets all interfaces on the device, including type, name, status, and description"""
        return (self.SSHConnection.send_command("show interfaces", use_textfsm=True))
    
    def get_interface_detail(self, type, interface):
        """Gets Linux style details of the specified interface, including addreses, RX, TX, etc."""

        if self.validate_interface_parms(type, interface):
            return (self.SSHConnection.send_command("show interfaces {} {}".format(type, interface)))

    def validate_interface_parms(self, type: str, interface: str) -> str:
        valid_types = [   # all valid interface types
            "ethernet", "loopback", "wireguard", "bonding", "bridge", "dummy","ethernet","input","l2tpv3",
            "loopback","openvpn","pseudo-ethert" ,"tunnel","vti","vxlan","wireguard","wireless","wirelessmodem"]

        while type not in valid_types:                                  # if the input is not in the list
            raise ValueError("""ValueError: Invalid Interface Type;
            Must be Ethernet,  """)                                  # return value error
        self.validate_is_string(interface)                           # validate that the interface is a string
        return True                                                  # if no value errors, return the inputs

    def get_changed(self):
        return (self.SSHConnection.send_command("compare"))

    def run_ping(self, target, count):
        return (self.SSHConnection.send_command(f"ping {target} count {count}"))

    # enable interface (delete disable)
    def delete_disable_interface(self, interface_type, interface_name):
        self.SSHConnection.config_mode()
        self.SSHConnection.send_command(f"delete interfaces {interface_type} {interface_name} disable")
    
    def compare(self):
        return self.SSHConnection.send_command("compare")

    # def get_ping_data(self, target, count):
    #     final = []

    #     raw = self.run_ping(target, count) # runs ping command, with a count of 10 packets

    #     # uses regex to specific find the ping data
    #     result = re.findall(r"^PING\b[^(]*\(([^)]*)\)\s([^.]*)\..*?^(\d+\sbytes).*?icmp_seq=(\d+).*?ttl=(\d+).*?time=(.*?ms).*?(\d+)\spackets\stransmitted.*?(\d+)\sreceived.*?(\d+%)\spacket\sloss.*?time\s(\d+ms).*?=\s([^\/]*)\/([^\/]*)\/([^\/]*)\/(.*?)\sms", raw, re.MULTILINE|re.DOTALL)

    #     print (result)

    #     final.extend([
    #         result[0][0],             # target
    #         float(result[0][8][:-1]), # packet loss
    #         float(result[0][10]),     # min
    #         float(result[0][11]),     # avg
    #         float(result[0][12]),     # max
    #         float(result[0][13]),     # std_dev
    #         self.host,                # hostname
    #     ])

    #     # final.extend( [[(result[0][0]), float(result[0][11])]] )

    #     return (final) # returns the final array of ping times and destination, as floats


    def get_ping_graph(self, target, requests, export):
        x = []
        y = []
        for i in range (0, requests):
            raw = (self.run_ping(target, 1))
            results = re.findall(r"^PING\b[^(]*\(([^)]*)\)\s([^.]*)\..*?^(\d+\sbytes).*?icmp_seq=(\d+).*?ttl=(\d+).*?time=(.*?ms).*?(\d+)\spackets\stransmitted.*?(\d+)\sreceived.*?(\d+%)\spacket\sloss.*?time\s(\d+ms).*?=\s([^\/]*)\/([^\/]*)\/([^\/]*)\/(.*?)\sms", raw, re.MULTILINE|re.DOTALL)
            print ("Ping :", results[0][11], "ms")
            x.append (int(i))
            y.append (float(results[0][11]))
            
            plt.plot (x, y, marker='o', color='red', label='Ping')
            plt.xticks(x)
            title = ("Ping to {} ({}) on {}".format(results[0][0],target,(self.host)))
            plt.title (title)
            plt.ylabel('Response time (ms)')
            plt.xlabel('ICMP packets transmitted')

        if export == "show":
            plt.show()

        if export == "save":
            plt.savefig(f"{self.host}-{target}-ping.png")
            plt.close()
            print ("Saved Graph")

    ### start of config generation methods

    def gen_hostname(hostname):
        j2template = ("set system host-name {{ hostname }}")
        output = Template(j2template)                                
        rendered = (output.render(hostname=hostname))                
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_int(conf):
        """
        :param state: disabled, disables interface
                    : deleted,  deletes interface
                    : present,     interface remains
        """

        output = Template(j2templates.vyos_int)                      
        rendered = (output.render(interfaces=conf))                  
        return Main.conv_jinja_to_arr(rendered)                      

    def gen_wireguard_int(state, type, name, ip, mask, desc, firewall, 
                            port, privkey, wg_peers):
        """
        :param state: disabled, disables interface
                    : deleted,  deletes interface
                    : present,     interface remains
        """
        output = Template(j2templates.vyos_wireguard_int)                      
        rendered = output.render(state=state, name=name, type=type, ip=ip, mask=mask,
                                    desc=desc, firewall=firewall, port=port, privkey=privkey,
                                        wg_peers=wg_peers)
        return Main.conv_jinja_to_arr(rendered)

    def gen_ospf(ospf):
        output = Template(j2templates.vyos_ospf)                     
        rendered = (output.render(ospf=ospf))
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_bgp_peer(peers, localAS):
        output = Template(j2templates.vyos_bgp_peer)                 
        rendered = (output.render(peers=peers, localAS=localAS))     
        return (Main.conv_jinja_to_arr(rendered))                    
    
    def gen_bgp_prefixes(prefixes, localAS):
        output = Template(j2templates.vyos_bgp_prefixes)             
        rendered = (output.render(prefixes=prefixes, localAS=localAS))
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_route_map(route_maps):
        output = Template(j2templates.vyos_routemap)                 
        rendered = (output.render(route_maps=route_maps))            
        return (Main.conv_jinja_to_arr(rendered))                    


    def gen_prefix_list(prefix_lists):
        output = Template(j2templates.vyos_prefix_list) 
        rendered = (output.render(prefix_lists=prefix_lists))        
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_static(static_routes):
        output = Template(j2templates.vyos_static)                                 
        rendered = (output.render(static=static_routes))              
        return (Main.conv_jinja_to_arr(rendered))                     


    def gen_firewalls(firewalls):
        output = Template(j2templates.vyos_firewall)               
        rendered = (output.render(firewalls=firewalls))            
        return (Main.conv_jinja_to_arr(rendered))                  

    def gen_zones(zones):
        output = Template(j2templates.vyos_zones)                  
        rendered = (output.render(zones=zones))                    
        return (Main.conv_jinja_to_arr(rendered))                  

    def gen_dhcp(dhcp):
        output = Template(j2templates.vyos_dhcp)                   
        rendered = (output.render(dhservers=dhcp))                 
        return (Main.conv_jinja_to_arr(rendered))                  
    
    def set_lldp(self, interfaces, legacy_protocols) -> str:
        output = Template(j2templates.vyos_lldp)
        rendered = (output.render(interfaces=interfaces,
                                  legacy_protocols=legacy_protocols)) 
        return (Main.conv_jinja_to_arr(rendered))

    def deploy_yaml(ymlfile):

        with open(ymlfile) as file: # opens the yaml file
            raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var
            
        for device in raw["routers"]:
            print ("----", device["name"],"----")

            to_deploy = []

            # if key exists in yaml file
            # get generated config and append to array "to.deploy"

            hostname = device.get("name")               
            if hostname != None:                                                   
                to_deploy.append (Vyos.gen_hostname(hostname))                     

            interfaces = device.get("interfaces")
            if interfaces != None:
                to_deploy.append (Vyos.gen_int(interfaces))

            wireguard_interfaces = device.get("wireguard_interfaces")
            if wireguard_interfaces != None:
                for wg_int in wireguard_interfaces:
                    rendered =  (Vyos.gen_wireguard_int(wg_int["state"], wg_int["type"], wg_int["name"], wg_int["ip"], wg_int["mask"],
                                                                    wg_int["desc"], wg_int["firewall"], wg_int["port"],
                                                                       os.environ.get(wg_int["privkey"]), wg_int["wg_peers"]))
                    to_deploy.append(rendered)

            bgpasn = device.get("bgpasn")
            bgp_peers = device.get("bgp_peers")

            if bgpasn != None and bgp_peers != None:
                to_deploy.append (Vyos.gen_bgp_peer(bgp_peers, bgpasn))
            
            bgp_prefixes = device.get("bgp_prefixes")
            if bgp_prefixes != None:
                to_deploy.append (Vyos.gen_bgp_prefixes(bgp_prefixes, bgpasn))

            route_maps = device.get("route_maps")
            if route_maps != None:
                to_deploy.append (Vyos.gen_route_map(route_maps))

            prefix_lists = device.get("prefix_lists")
            if prefix_lists != None:
                to_deploy.append (Vyos.gen_prefix_list(prefix_lists))

            ospf = device.get("ospf")
            if ospf != None:
                to_deploy.append (Vyos.gen_ospf(ospf))
            
            firewalls = device.get("firewalls")
            if firewalls != None:
                to_deploy.append(Vyos.gen_firewalls(firewalls))

            static_routes = device.get("static")
            if static_routes != None:
                to_deploy.append(Vyos.gen_static(static_routes))

            dhservers = device.get("dhcp")
            if dhservers != None:
                to_deploy.append(Vyos.gen_dhcp(dhservers))

            print("----------------------------")
            print("TO DEPLOY")
            print("----------------------------")
            for i in to_deploy:  # loops through command arrays
                for j in i:
                    print (j)    # and prints them
            print("----------------------------")

            router = Vyos(
                device_type = "vyos",
                host = device["SSH_conf"]["hostname"],
                username = device["SSH_conf"]["username"],
                password = device["SSH_conf"]["password"],
                use_keys = device["SSH_conf"]["use_keys"],
                key_file = device["SSH_conf"]["key_location"],
                
            )

            Vyos.init_ssh(router)               # starts the SSH connection
            Vyos.config_mode(router)            # enters Vyos config mode

            print ("----------------------------")
            print ("Sending Commands, please wait")
            print ("----------------------------")
            for i in to_deploy:                 # for every code block generated (every 1st dimension in arr)
                Vyos.bulk_commands(router, i)   # send commands over SSH
            print ("----------------------------")
            print ("Commands Sent")
            print ("----------------------------")
            print ("Diff/Changes:")
            print ("----------------------------")
            print (Vyos.get_changed(router))       # sends "compare" command
            print ("----------------------------")
            print ("Committing Changes")
            Vyos.commit(router)
            print ("Changes Committed, Success")


class EdgeOS(Vyos):  # Vyos/EdgeOS specific commands

    # inherits all methods and attributes from the MAIN class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # calls the __init__ method from the  superclass, creating the netmiko SSH tunnel

    def bulk_commands(self, commands):
        self.SSHConnection.config_mode()
        return (self.SSHConnection.send_config_set(commands))

    def get_interfaces(self):
        return (self.SSHConnection.send_command("show interfaces ethernet", use_textfsm=True))

    def run_ping(self, target, count):
        return (self.SSHConnection.send_command(f"sudo ping -c {count} {target}"))

    def get_changed(self):
        return (self.SSHConnection.send_command("compare"))

    def save_config(self):
        return self.SSHConnection.send_command("save")

    def config_mode(self):
        self.SSHConnection.config_mode()

    def discard_changes(self):
        return (self.SSHConnection.send_command("discard"))

    def commit(self):
        self.SSHConnection.commit()
        return ("Committed")

    # GEN METHODS

    def set_lldp(self, interfaces, legacy_protocols) -> str:
        output = Template(j2templates.edgeos_lldp)
        rendered = (output.render(interfaces=interfaces,
                                  legacy_protocols=legacy_protocols)) 
        return (Main.conv_jinja_to_arr(rendered))

    def gen_int(conf):
        """
        :param state: disabled, disables interface
                    : deleted,  deletes interface
                    : else,     interface remains
        """

        output = Template(j2templates.edgeos_int)
        rendered = (output.render(interfaces=conf))
        return Main.conv_jinja_to_arr(rendered)

    def deploy_yaml(ymlfile):

        with open(ymlfile) as file: # opens the yaml file
            raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var
            
        for device in raw["routers"]:
            print ("----", device["name"],"----")

            to_deploy = []

            hostname = device.get("name")               
            if hostname != None:                                                   # if key exists in yaml file
                to_deploy.append (EdgeOS.gen_hostname(hostname))                     # get generated config and append to array "to.deploy"

            interfaces = device.get("interfaces")
            if interfaces != None:
                to_deploy.append (EdgeOS.gen_int(interfaces))

            bgpasn = device.get("bgpasn")
            bgp_peers = device.get("bgp_peers")

            if bgpasn != None and bgp_peers != None:
                to_deploy.append (EdgeOS.gen_bgp_peer(bgp_peers, bgpasn))
            
            bgp_prefixes = device.get("bgp_prefixes")
            if bgp_prefixes != None:
                to_deploy.append (EdgeOS.gen_bgp_prefixes(bgp_prefixes, bgpasn))

            route_maps = device.get("route_maps")
            if route_maps != None:
                to_deploy.append (EdgeOS.gen_route_map(route_maps))

            prefix_lists = device.get("prefix_lists")
            if prefix_lists != None:
                to_deploy.append (EdgeOS.gen_prefix_list(prefix_lists))

            ospf = device.get("ospf")
            if ospf != None:
                to_deploy.append (EdgeOS.gen_ospf(ospf))
            
            firewalls = device.get("firewalls")
            if firewalls != None:
                to_deploy.append(EdgeOS.gen_firewalls(firewalls))

            static_routes = device.get("static")
            if static_routes != None:
                to_deploy.append(EdgeOS.gen_static(static_routes))

            dhservers = device.get("dhcp")
            if dhservers != None:
                to_deploy.append(EdgeOS.gen_dhcp(dhservers))


            zones = device.get("zones")
            if zones != None:
                to_deploy.append(EdgeOS.gen_zones(zones))

            print("----------------------------")
            print("TO DEPLOY")
            print("----------------------------")
            for i in to_deploy:  # loops through command arrays
                for j in i:
                    print (j)    # and prints them
            print("----------------------------")

            router = EdgeOS(
                device_type = "ubiquiti_edgerouter",
                host = device["SSH_conf"]["hostname"],
                username = device["SSH_conf"]["username"],
                password = device["SSH_conf"]["password"],
                use_keys = device["SSH_conf"]["use_keys"],
                key_file = device["SSH_conf"]["key_location"],
            )

            EdgeOS.init_ssh(router)               # starts the SSH connection
            EdgeOS.config_mode(router)            # enters Vyos config mode

            print ("----------------------------")
            print ("Sending Commands, please wait")
            print ("----------------------------")
            for i in to_deploy:                 # for every code block generated (every 1st dimension in arr)
                EdgeOS.bulk_commands(router, i)   # send commands over SSH
            print ("----------------------------")
            print ("Commands Sent")
            print ("----------------------------")
            print ("Diff/Changes:")
            print ("----------------------------")
            print (EdgeOS.get_changed(router))       # sends "compare" command
            print ("----------------------------")
            print ("Committing Changes")
            EdgeOS.commit(router)
            print ("Changes Committed, Success")

class Cisco_IOS(Main):  # cisco specific commands

    # inherits all methods and attributes from MAIN class
    # sends 'cisco_ios' as an argument, so user doesn't have to specify device_type
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
        output = Template(j2templates.ios_vlan)
        rendered = (output.render(vlans=vlans)) 
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_int(interfaces):
        output = Template(j2templates.ios_int)
        rendered = (output.render(interfaces=interfaces))            
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_hostname(hostname):
        j2template = "hostname {{ hostname }}"                       
        output = Template(j2template)                                
        rendered = (output.render(hostname=hostname))                
        return (Main.conv_jinja_to_arr(rendered))                    

    def gen_ospf_networks(networks):                      
        output = Template(j2templates.ios_ospf)                      
        rendered = (output.render(networks=networks))                
        return (Main.conv_jinja_to_arr(rendered))                    

    def set_lldp(self, run:bool) -> list:
        output = Template(j2templates.ios_lldp)                      
        rendered = (output.render(run=run)) 
        return (Main.conv_jinja_to_arr(rendered))                    

    def lint_yaml(ymlfile):
        with open(ymlfile) as file: # opens the yaml file
            raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var

            print(raw)

    def deploy_yaml(ymlfile):

        with open(ymlfile) as file: # opens the yaml file
            raw = yaml.safe_load(file)    # reads and stores the yaml file in raw var

        for device in raw["devices"]:
            print ("----", device["name"],"----")

            to_deploy = []

            hostname = device.get("name")               
            if hostname != None:                                                # if key exists in yaml file
                to_deploy.append (Cisco_IOS.gen_hostname(hostname))             # generate command and append to array

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

            router1 = Cisco_IOS(
                device_type = "cisco_ios",
                host = device["SSH_conf"]["hostname"],
                username = device["SSH_conf"]["username"],
                password = device["SSH_conf"]["password"],
                use_keys = device["SSH_conf"]["use_keys"],
                key_file = device["SSH_conf"]["key_location"],
                secret = device["SSH_conf"]["secret"],
            )
            Cisco_IOS.init_ssh(router1)               # starts the SSH connection

            running_conf_before = Cisco_IOS.get_all_config(router1)

            print ("----------------------------")
            print ("Sending Commands, please wait")
            for command in to_deploy:                       # for every code block generated (every dimension in arr)
                Cisco_IOS.bulk_commands(router1, command)   # send commands over SSH
            print ("----------------------------")
            print ("Commands Sent, success")
            print ("----------------------------")
            print ("Diff/Changes:")
            running_conf_after = Cisco_IOS.get_all_config(router1)
            print (Main._unidiff_output(running_conf_before, running_conf_after))
            print ("----------------------------")