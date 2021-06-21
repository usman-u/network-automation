from netmiko import Netmiko,ConnectHandler
import getpass, datetime

SW1 = {
    'device_type': 'cisco_ios',
    'host':   '',
    'username': '',
    'password': '',
    'secret': '',
}

devices = [SW1] 

def backup(devices):
    for device in devices: 
        main_time = datetime.datetime.now()
        string_time = str(main_time.strftime("%x"))
        if device["username"] == "":
            (device["username"]) = getpass.getpass(prompt="No Host Data; Enter SSH Username: " )
        if device["password"] == "":
            (device["password"]) = getpass.getpass(prompt="No Host Data Enter SSH Password: ")
        if device["secret"] == "":
            (device["secret"]) = getpass.getpass(prompt="No Host Data Enter Secret for: ")

        net_connect = ConnectHandler(**device) # connects to current device iteration
        print ("Connected to: "+device["host"])
        net_connect.enable()  # runs the enable command 
        
        show_run = net_connect.send_command("show run")
        show_vlan = net_connect.send_command("show vlan") 
        sh_ints = net_connect.send_command("show ip int br") 
        sh_version = net_connect.send_command("show version", use_textfsm=True)
        sh_ints_desc = net_connect.send_command("show interfaces description")

        hostname = sh_version[0]['hostname']  # gets data from initial dict
        IPaddr = device['host']

        print("Backing up " + hostname + string_time) 

        fileName = (hostname + "-" + IPaddr + "-" + "Backup")# generates filename from initial dict
        #fileName = (hostname)# generates filename from initial dict

        contents = (show_run +"\n"+ show_vlan +"\n"+ sh_ints +"\n"+ sh_ints_desc) 

        f = open(fileName, "x") # opens in (w)rite mode, to overwrite existing contents, instead of (a)ppend 
        f.write(contents)

        print ("Wrote File: " + fileName)
        f.close()
        net_connect.disconnect()

def MainMenu():
    selection = input("Choose an option:\n 1: Backup Config: ") 
    while selection != "1":
        selection = input("Invalid Input!\n Choose an option:\n 1: Backup Config\n") 
    
    if selection == "1":
        backup(devices)

MainMenu()