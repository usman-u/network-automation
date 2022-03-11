from jinja2 import Template

data = [
    ["10", "10desc","10.0.10.1", "255.255.255.0"],
    ["20", "10desc","10.0.10.1", "255.255.255.0"]
]
file = open("vlans.j2", "r")

temp = Template(file.read())
# print (jtemplate.render(vlan = "5", vlandesc = "five", ip = "10.0.10.1", mask = "255.255.255.0"))
for i in data:
    print ("---")
    print (temp.render(vlan = i[0], vlandesc = i[1], ip = i[2], mask = i[3]))