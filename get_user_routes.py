#!/usr/bin/env python
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contributors:
# jdow@mozilla.com
#
# Requires:
# libnfldap
# netaddr

import os
import sys
import pwd
import imp
import struct
from lib.helper import cidr_to_netmask, squash_routes, remove_office_routes, ldap_routes_not_in_config,\
    standardize_acls
import libnfldap


def main():
    cfg_path = ['get_user_routes.conf', '/usr/local/etc/get_user_routes.conf', '/etc/get_user_routes.conf']
    config = None

    for cfg in cfg_path:
        if os.path.isfile(cfg):
            try:
                config = imp.load_source('config', cfg)
            except:
                pass

    if config == None:
        print("Failed to load config")
        sys.exit(1)

    try:
        username = sys.argv[1]
    except IndexError:
        print ("Need one argument, email-username")
	sys.exit (1)

    # if the user is connecting from an office, we need to know, so that we can filter out local destinations
    try:
        if sys.argv[2] == "--office":
            from_office=1
        else:
            from_office=0
    except IndexError:
        from_office=0

    # currently using libnfldap, since it has a function to get all the ACLs for a group
    ldap = libnfldap.LDAP(config.LDAP_URL, config.LDAP_BIND_DN, config.LDAP_BIND_PASSWD)

    filterk = '(mail='+username+')'
    query = filterk
    res = ldap.query('dc=mozilla', query, ['mail'])
    dn = res[0][0]


    # find all vpn groups user is in and return IP attributes
    acls = ldap.getACLs('ou=groups,dc=mozilla',"(&(member="+dn+")(cn=vpn_*))")
    ips = standardize_acls(acls)
    ldap_routes = ldap_routes_not_in_config(ips, config.ROUTES)


    # merge user-specific routes with routes from the config, only unique. Sorted for human readability
    all_routes = sorted(set(config.ROUTES + ldap_routes + config.OFFICE_ROUTES))

    # check that there are no overlapping routes, remove office routes if connecting from an office
    if from_office == 1:
        squashed_routes = remove_office_routes(squash_routes(all_routes),config.OFFICE_ROUTES)
    else:
        squashed_routes = squash_routes(all_routes)

    #Finally, we need to output all the routes in a nice list that bash will be able to iterate over
    for address in squashed_routes:
        ip, mask = cidr_to_netmask(address)
        # For one entry per line, remove the trailing comma
        print("{ip} {mask}").format(ip=ip, mask=mask)

if __name__ == "__main__":
    main()
