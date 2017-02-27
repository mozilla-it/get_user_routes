import socket
import struct
from netaddr import IPNetwork, IPAddress

def cidr_to_netmask(cidr):
    network, net_bits = cidr.split('/')
    host_bits = 32 - int(net_bits)
    netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
    return network, netmask

# function to remove more specific routes when less specific routes exist
def squash_routes(listofroutes):
    returnlist = []
    # build a list of routes, ignoring single-host routes
    notsinglehosts = []
    for route in listofroutes:
        if not route.find('/32') != -1:
            notsinglehosts.append(route)
    # Check every route against the list of non-single-host routes
    for route in listofroutes:
        for notsinglehost in notsinglehosts:
            #check each route in the master list against the non-single host routes, but don't match against self
            if IPNetwork(route) in IPNetwork(notsinglehost) and route != notsinglehost:
                break
        # if we went through the list without a match, add it to the final return list
        else:
            returnlist.append(route)
    return_list_set = set(returnlist)
    return sorted([l for l in return_list_set])

# function to filter out routes for destinations within office space
def remove_office_routes(listofroutes,office_routes):
    returnlist = []
    # Check every route against the list of office routes
    for route in listofroutes:
        for office_route in office_routes:
            #check each route in the master list against the non-single host routes, but don't match against self
            if IPNetwork(route) in IPNetwork(office_route):
                break
        # if we went through the list without a match, add it to the final return list
        else:
            returnlist.append(route)
    return returnlist
