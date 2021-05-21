from netmiko import Netmiko
from netmiko import ConnectHandler


ERX = {
    'device_type': 'ubiquiti_edgerouter',
    'host':   '192.168.0.1',
    'username': '',
    'password': '',
}

devices = [ERX]

for x in devices:
    hostname = (x["host"])

    net_connect = ConnectHandler(**x)    # x is the current index/device
    shver = net_connect.send_command('show version')                             # sends ssh
    shconfig = net_connect.send_command('show configuration')                    # commands
    shconfigcommands = net_connect.send_command('show configuration commands')   # via netmiko

    fileName = ("Backup " + hostname)      # creates new file
    f = open((fileName), "w")  # opens in (w)rite mode, to overwrite existing contents, instead of (a)ppend 
    
    contents = (shver +"\n"+ shconfig +"\n"+ shconfigcommands)
    f.write(contents) # writes the commands format to file

    print ("Wrote File: " + fileName) 
    f.close()

    net_connect.disconnect() 