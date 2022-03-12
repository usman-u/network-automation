import yaml
from jinja2 import Template

with open("devices.yml") as file:
    
    raw = yaml.safe_load(file)

    #for i in range (0, len(raw['devices'])):  # in devices
        #print (raw['devices'][i]['name'])
        #print ("---")
        #print (raw['devices'][i]['interfaces'][1]) # 0 is ethernet, 1 is loopback

with open("cisco_router.j2") as file:
    template = Template(file.read())

#iterate over the devices described in your yaml file
#and use jinja to render your configuration
for device in raw["routers"]:
    print(
    template.render(device=device["name"],
    interfaces=device["interfaces"], 
    bgpasn=device["bgpasn"], 
    bgp_neighbors=device["bgp_neighbors"],
    ospf_pid=device["ospf_pid"],
    ospf_networks=device["ospf_networks"],
    ospf_routerid=device["ospf_routerid"],
    use_ospf_routerid = device["use_ospf_routerid"],
    )
)
