from os import device_encoding
from netmiko import Netmiko, ConnectHandler
import netmiko

class Main():

    def __init__(self, device_type, host, username, password, use_keys, key_file, secret):
        self.device_type = device_type
        self.host = host
        self.username = username
        self.password = password
        self.use_keys = use_keys
        self.key_file = key_file
        self.secret = secret

        # netmiko template for device    
        self.data = {

            'device_type': self.device_type,
            'host':   self.host,
            'username': self.username,
            'password': self.password,
            'use_keys': self.use_keys,
            'key_file': self.key_file,

        }

        # connects to the device via ssh
        print("Connecting to", self.host, "via SSH")
        self.SSHConnection = ConnectHandler(**self.data)
        print("Connected")

    def printData(self):
        return self.data

    def getconfig(self):

        config = self.SSHConnection.send_command(f'show configuration')
        self.write_file(config)
        
    def write_file(self, contents):

        fileName = (self.device_type + self.host)

        file = open((fileName), "w") 
        file.write(contents)

        print ("Wrote File", fileName)
        file.close()
    
    def bgp_neighbors(self, neighbor):

        neighbors = self.SSHConnection.send_command("show ip bgp neighbors")
        return neighbors

    def route_table(self):

        routes = self.SSHConnection.send_command("show ip route")
        return (routes)

    def version(self):
        
        version = self.SSHConnection.send_command("show version")
        return version

    def ping(self, target):

        ping = self.SSHConnection.send_command(f"ping {target} -t 5")
        return ping

    def traceroute(self, target):
        
        print ("Running traceroute to", target)
        traceroute = self.SSHConnection.send_command("traceroute 1.1.1.1")
        return traceroute

# creates an instance of the MAIN class with arguments, and connects via SSH
erx1 = Main("", "", "", "", True, r"C:\Users\Usman\.ssh\id_rsa", "")

ciscosw1 = Main("", "", "", "", False, r"C:\Users\Usman\.ssh\id_rsa", "")

devices = [erx1]

for i in devices:
    print (Main.version(i))