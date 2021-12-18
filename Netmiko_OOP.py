from netmiko import Netmiko, ConnectHandler

class Main():

    # attributes are standard for netmiko functionality
    def __init__(self, device_type, host, username, password, use_keys, key_file, secret):
        self.device_type = device_type
        self.host = host
        self.username = username
        self.password = password
        self.use_keys = use_keys
        self.key_file = key_file
        self.secret = secret

        # netmiko template for network device parameters
        # uses first if statement if the user has a ssh private key file
        # second if using username password auth

        if self.use_keys == True:

            self.data = {

                'device_type': self.device_type,
                'host':   self.host,
                'username': self.username,
                'password': self.password,
                'use_keys': self.use_keys,
                'key_file': self.key_file,

            }
        
        elif self.use_keys == False:

            self.data = {

                'device_type': self.device_type,
                'host':   self.host,
                'username': self.username,
                'password': self.password,

            }

        # connects to the device via ssh
        print("Connecting to", self.host, "via SSH")
        self.SSHConnection = ConnectHandler(**self.data)
        print("Connected to", self.host, "via SSH")

    # vendor neutral methods - common commands are syntaxically identical on various network systems

    def printData(self):
        return self.data

    def write_file(self, contents):

        fileName = (self.device_type + self.host)

        file = open((fileName), "w") 
        file.write(contents)

        print ("Wrote File", fileName)
        file.close()

    def get_version(self):
        
        result = self.SSHConnection.send_command("show version")
        return result

    def run_ping(self, target):

        result = self.SSHConnection.send_command(f"ping {target} -t 5")
        return result

    def run_traceroute(self, target):
        
        print ("Running traceroute to", target)
        result = self.SSHConnection.send_command("traceroute 1.1.1.1")
        return result

class EdgeRouter(Main):  # Vyos/EdgeOS specific commands

    # inherits all methods and attributes from the MAIN class
    def __init__(self, device_type, host, username, password , use_keys, key_file, secret):
        super().__init__(device_type, host, username, password, use_keys, key_file, secret)
        # calls the __init__ function from the MAIN superclass, creating the netmiko SSH tunnel
    
    def get_config(self):

        result = self.SSHConnection.send_command(f'show configuration')
        return result
        
    def get_config_commands(self):

        result = self.SSHConnection.send_command(f'show configuration commands')
        return result
    
    def get_bgp_neighbors(self, neighbor):

        result = self.SSHConnection.send_command("show ip bgp neighbors")
        return result

    def get_route_table(self):

        result = self.SSHConnection.send_command("show ip route", use_textfsm=True)
        return result

    def get_interfaces(self):

        result = self.SSHConnection.send_command("show interfaces", use_textfsm=True)
        return result

class Cisco_IOS(Main):  # cisco specific commands

    # inherits all methods and attributes from MAIN class
    def __init__(self, device_type, host, username, password , use_keys, secret):
        super().__init__(device_type, host, username, password, use_keys, secret)
        # calls the __init__ function from the MAIN superclass, creating the netmiko SSH tunnel
    
    def get_config(self):

        result = self.SSHConnection.send_command(f'show run')
        return result
    
    def get_route_table(self):

        result = self.SSHConnection.send_command("show ip route")
        return result
    
    def get_interfaces_brief(self):

        result = self.SSHConnection.send_command("show ip interface brief")
        return result

    def get_interfaces(self):

        result = self.SSHConnection.send_command("show ip interface")
        return result