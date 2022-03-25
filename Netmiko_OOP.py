from jinja2 import Template
from netmiko import Netmiko, ConnectHandler
import datetime
import os

template_path = "C:\\Users\\Usman\\Desktop\\projects\\network-automation\\j2templates"
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
    
    def bulk_commands(self, commands):
        return (self.SSHConnection.send_config_set(commands))
    
    def get_config(self):
        return (self.SSHConnection.send_command(f'show configuration'))
        
    def get_config_commands(self):
        return (self.SSHConnection.send_command(f'show configuration commands'))
    
    def get_bgp_neighbors(self):
        return (self.SSHConnection.send_command("show ip bgp summary"))

    def get_interfaces(self):
        return (self.SSHConnection.send_command("show interfaces"))

    # enable interface (delete disable)
    def delete_disable_interface(self, interface_type, interface_name):
        self.SSHConnection.config_mode()
        self.SSHConnection.send_command(f"delete interfaces {interface_type} {interface_name} disable")
    
    def compare(self):
        return self.SSHConnection.send_command("compare")

    def save_config(self):
        commands = ["save"]
        self.SSHConnection.send_config_set(commands)

    def commit(self):
        self.SSHConnection.commit()
        print ("committed")

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

class GenVyos():
    def gen_int(conf):
        os.chdir(template_path+vyos_folder) # navigates to dir containing vyos templates
        raw = open("gen_int.j2")            # opens j2 file
        j2template = raw.read()             # processes file
        raw.close()                         # closes file
        output = Template(j2template)
        return (output.render(interfaces=conf)) # interfaces var is defined in the jinja template file

    def gen_ospf_networks(networks):
        os.chdir(template_path+vyos_folder)
        raw = open("gen_ospf_network.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        return (output.render(networks=networks))

    def gen_bgp_peer(peers, localAS):
        os.chdir(template_path+vyos_folder)
        raw = open("gen_bgp_peer.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        return (output.render(peers=peers, localAS=localAS))
    
    def gen_bgp_prefixes(prefixes):
        os.chdir(template_path+vyos_folder)
        raw = open("gen_bgp_prefixes.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        return (output.render(prefixes=prefixes))

class GenCisco():        # class for generating configurations using Jinja2
    def gen_vlan(vlan):
        os.chdir(template_path+cisco_folder)
        raw = open("gen_vlan.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        return (output.render(vlan=vlan)) 

    def gen_int(interfaces):
        os.chdir(template_path+cisco_folder)
        raw = open("gen_int.j2")
        j2template = raw.read()
        output = Template(j2template)
        raw.close()
        return (output.render(interfaces=interfaces)) # left interfaces var in j2 file,


class BIRD(Main):  # cisco specific commands

    # inherits all methods and attributes from MAIN class
    # sends 'linux' as an argument, so user doesn't have to specify device_type
    def __init__(self, host, username, password , use_keys, key_file, secret):
        super().__init__("linux", host, username, password, use_keys, key_file, secret)
        # calls the __init__ function from the MAIN superclass, creating the netmiko SSH tunnel
    
    def get_bgp_route(self, target):
        return (self.SSHConnection.send_command(f"sudo su; birdc show ip bgp {target}"))

    # TODO fix BIRD multi-line command (login as root for birdc)
    def get_birdc_protocols(self):
        return (self.SSHConnection.send_command(f"""
        sudo su
        birdc show protocols
    """))

    def run_traceroute(self, target):
        return (self.SSHConnection.send_command(f"traceroute {target}"))