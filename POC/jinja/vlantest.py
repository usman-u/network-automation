from jinja2 import Template

data = [
    ["10", "10desc","10.0.10.1", "255.255.255.0"],
    ["20", "10desc","10.0.10.1", "255.255.255.0"]
]

# print (jtemplate.render(vlan = "5", vlandesc = "five", ip = "10.0.10.1", mask = "255.255.255.0"))
# file = open("vlan-int.j2", "r")

with open('vlan-int.j2') as file:
    vlanTemplate= Template(file.read())
    for i in data:
        print ("---")
        print (vlanTemplate.render(vlan = i[0], vlandesc = i[1], ip = i[2], mask = i[3]))
