from Netmiko_OOP import *


# creates an instance of the MAIN class with arguments, and connects via SSH
erx1 = Main("ubiquiti_edgerouter", "erx.lan", "usman", "t", False , r"C:\Users\Usman\.ssh\id_rsa", "")

#ciscosw1 = Main("", "", "", "", False, r"C:\Users\Usman\.ssh\id_rsa", "")

devices = [erx1]

for i in devices:
    Main.write_file(i, Main.version(i))
    # print(Main.version(i))