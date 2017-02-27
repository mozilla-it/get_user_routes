import socket
import struct
from netaddr import IPNetwork

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

#Now that we have a list of all possible addresses that a user may access, we need to check
# if any aren't already covered by the default list of routes from the config.
def ldap_routes_not_in_config(ips,config_routes):
    notfoundlist = []
    for address in ips:
        for route in config_routes:
            if IPNetwork(address) in IPNetwork(route):
                break
        else:
            notfoundlist.append(address)
    return notfoundlist

#function to parse through all ldap ACLs and return a standard format in cidr notation, stripping port information
def standardize_acls(acls):
    ips = []
    for group,dests in acls.iteritems():
        for dest,desc in dests.iteritems():
            # strip off port information
            ip = dest.split(":")[0]
            # if address is already in cidr format, add it, else assume single host IP and add /32
            # this is in order to keep a consistent format for all addresses before we process
            if ip.find('/') != -1:
                ips.append(ip)
            else:
                ips.append(ip+'/32')
    return ips
