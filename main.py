from Netmiko_OOP import *        # imports all classes & methods from Netmiko.py

###
example_device = Cisco_IOS(
    "hostname",
    "username",
    "password", 
    False,                          # connect using SSH keys 
    r"C:\Users\Usman\.ssh\id_rsa",  # SSH private key location
    "")                             # cisco ios secret
###

# creates an instance of the Main class with arguments, which connects to the device (via SSH)
# and stores the instance in a variable
usmancisco = Cisco_IOS(
    "usman-cisco.lan",
    "usman",
    "", 
    False, 
    "", 
    "")

zahidcore = Cisco_IOS(
    "zahid-core.lan",
    "usman",
    "", 
    False, 
    "", 
    "")

usmanerx = Main(
    "ubiquiti_edgerouter", 
    "usman-erx.lan", 
    "usman", 
    "", 
    True, 
    r"C:\Users\Usman\.ssh\id_rsa", 
    "")

zahiderx = Main(
    "ubiquiti_edgerouter", 
    "zahid-erx.lan", 
    "usman", 
    "", 
    True, 
    r"C:\Users\Usman\.ssh\id_rsa", 
    "")


ciscodevices = [zahidcore, usmancisco]

for device in ciscodevices:                                                                 # iterates through the "cisco_devices" array and:
    to_write = Cisco_IOS.get_all_config(device) + "\n\n\n" + Cisco_IOS.get_version(device)  # stores the outputs from method in a "to_write"
    Cisco_IOS.write_file(device, to_write, "")                                              # writes the output to new files

ubiqutirouters = [zahiderx, usmanerx]

for device in ubiqutirouters:
    to_write = Vyos.get_config(device) + "\n\n\n" + Vyos.get_config_commands(device)
    Main.write_file(device, to_write, "")