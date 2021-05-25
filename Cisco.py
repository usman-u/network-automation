from netmiko import Netmiko,ConnectHandler
import getpass

SW1 = {
    'device_type': 'cisco_ios',
    'host':   '192.168.0.5',
    'username': '',
    'password': '',
    'secret': '',
}

devices = [SW1] 

for device in devices: 
    (device["username"]) = getpass.getpass(prompt='Enter SSH Username: ')
    (device["password"]) = getpass.getpass(prompt="Enter SSH Password: ")
    (device["secret"]) = getpass.getpass(prompt="Enter Secret Password: ")

    net_connect = ConnectHandler(**device) # connects to every device 
    net_connect.enable()  # runs the enable command 

    show_run = net_connect.send_command("show run")
    show_vlan = net_connect.send_command("show vlan") 
    sh_ints = net_connect.send_command("show ip int br") 
    sh_version = net_connect.send_command("show version", use_textfsm=True)
    sh_ints_desc = net_connect.send_command("show interfaces description")

    hostname = sh_version[0]['hostname']  # gets data from initial dict
    IPaddr = device['host']

    print("Backing up " + hostname) 

    fileName = (hostname + "-" + IPaddr + "-" + "Backup")      # generates filename from initial dict
    contents = (show_run +"\n"+ show_vlan +"\n"+ sh_ints +"\n"+ sh_ints_desc) 

    f = open((fileName), "w") # opens in (w)rite mode, to overwrite existing contents, instead of (a)ppend 
    f.write(contents)

    print ("Wrote File: " + fileName)
    f.close()
    net_connect.disconnect()