from Netmiko_OOP import *


# creates an instance of the MAIN class with arguments, and connects via SSH
# erx1 = Main("ubiquiti_edgerouter", "erx.lan", "usman", "t", False , r"C:\Users\Usman\.ssh\id_rsa", "")


# devices = [erx1]

# for i in devices:
#     Main.write_file(i, Main.version(i))
#     # print(Main.version(i))


erx1 = EdgeRouter("ubiquiti_edgerouter", "erx.lan", "usman", "", False , r"C:\Users\Usman\.ssh\id_rsa", "")
erx1.get_interfaces()

# print (erx1.write_file (str((erx1.printData()))))

# ciscosw1 = Cisco_IOS("cisco_ios", "cisco2960.lan", "admin", "", False, r"C:\Users\Usman\.ssh\id_rsa", "")


# ciscosw1 = Cisco_IOS("cisco_ios", "10.0.10.66", "usman", "", False, r"id_rsa", "")
# print (ciscosw1.show_ip_int_br())