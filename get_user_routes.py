#!/usr/bin/env python
"""
    This script's job is to print out a list of ROUTES that a user
    is entitled to have access to, and should be pushed upon VPN connect.

    This script is invoked as a second-tier script from our client-connect
    As such, we could have this script output pretty much anything we want
    so long as the message gets across.

    The output format is presently lines that look like:

    10.8.0.0 255.255.120.0

    Future thoughts:
        this should ship with a client-connect script.
        this should do a much smarter job of offering per-office routes.
"""
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contributors:
# gcox@mozilla.com
# jdow@mozilla.com
#
# Requires:
# iamvpnlibrary
# netaddr

import os
import sys
import ast
import iamvpnlibrary
from netaddr import IPNetwork, cidr_merge, cidr_exclude
sys.dont_write_bytecode = True
try:
    # 2.7's module:
    from ConfigParser import SafeConfigParser as ConfigParser
except ImportError:
    # 3's module:
    from configparser import ConfigParser

__all__ = ['GetUserRoutes']


class GetUserRoutes(object):
    """
        This is mainly implemented as a class because it's an easier way to
        keep track of our config-file based configuration.  For the most part
        this class acts as a utility that you query for information about a
        user.  In that sense, it's pretty close to a straightforward script.
    """
    CONFIG_FILE_LOCATIONS = ['get_user_routes.conf',
                             '/usr/local/etc/get_user_routes.conf',
                             '/etc/get_user_routes.conf']

    def __init__(self):
        """
            ingest the config file so other methods can use it
        """
        self.configfile = self._ingest_config_from_file()
        config = {}
        try:
            _freeroutes = ast.literal_eval(
                self.configfile.get('get-user-routes', 'FREE_ROUTES'))
        except:  # pylint: disable=bare-except
            # This bare-except is due to 2.7 limitations in configparser.
            _freeroutes = []
        try:
            _officeroutes = ast.literal_eval(
                self.configfile.get('get-user-routes',
                                    'COMPREHENSIVE_OFFICE_ROUTES'))
        except:  # pylint: disable=bare-except
            # This bare-except is due to 2.7 limitations in configparser.
            _officeroutes = []
        try:
            _perofficeroutes = ast.literal_eval(
                self.configfile.get('get-user-routes', 'PER_OFFICE_ROUTES'))
        except:  # pylint: disable=bare-except
            # This bare-except is due to 2.7 limitations in configparser.
            _perofficeroutes = {}
        config['FREE_ROUTES'] = [IPNetwork(routestr)
                                 for routestr in _freeroutes]
        config['COMPREHENSIVE_OFFICE_ROUTES'] = [IPNetwork(routestr)
                                                 for routestr in _officeroutes]
        config['PER_OFFICE_ROUTES'] = {office: IPNetwork(routestr)
                                       for office, routestr in
                                       _perofficeroutes.iteritems()}
        self.config = config

    def _ingest_config_from_file(self, conf_file=None):
        """
            pull in config variables from a system file
        """
        if conf_file is None:
            conf_file = self.__class__.CONFIG_FILE_LOCATIONS
        if isinstance(conf_file, basestring):
            conf_file = [conf_file]
        config = ConfigParser()
        for filename in conf_file:
            if os.path.isfile(filename):
                try:
                    config.read(filename)
                    break
                except:  # pylint: disable=bare-except
                    # This bare-except is due to 2.7
                    # limitations in configparser.
                    pass
        # Note that there's no 'else' here.  You could have no config file.
        # The init will assume default values where there's no config.
        return config

    @staticmethod
    def route_subtraction(myroutes, coverage_routes):
        """
            This script compacts a list of routes.
            Checks each route in A and removes it if a route in B covers it.
        """
        returnlist = []
        for myroute in myroutes:
            for coverage_route in coverage_routes:
                if myroute in coverage_route:
                    break
            else:
                returnlist.append(myroute)
        return returnlist

    @staticmethod
    def route_exclusion(myroutes, remove_routes):
        """
            This script shrinks route sizes.
            Checks each route in A and B's piece of it.
            Note that this is vastly different from route_subtraction
        """
        # This is a little twisty to read.  When you exclude a subnet
        # B from a larger subnet A, you end up with a list of smaller
        # subnets.  That means, if you have multiple B's, you need
        # to progressively keep the list A updated, so that each B is
        # removed from the ever-longer list of smaller A's.
        # This is probably overkill, since we only really do one extract
        # of B, but, just in case.
        if not isinstance(myroutes, list):
            myroutes = [myroutes]
        if not isinstance(remove_routes, list):
            remove_routes = [remove_routes]
        for remove_route in remove_routes:
            newroutelist = []
            for myroute in myroutes:
                newroutelist = (newroutelist +
                                cidr_exclude(myroute, remove_route))
            myroutes = newroutelist
        return sorted(list(set(myroutes)))

    def get_office_routes(self, from_office):
        """
            This should provide the routes that someone would have,
            based on if they're in/out of an office.
        """
        if isinstance(from_office, bool):
            if from_office:
                user_office_routes = []
            else:
                user_office_routes = self.config['COMPREHENSIVE_OFFICE_ROUTES']
        elif isinstance(from_office, basestring):
            if from_office in self.config['PER_OFFICE_ROUTES']:
                user_office_routes = self.route_exclusion(
                    self.config['COMPREHENSIVE_OFFICE_ROUTES'],
                    self.config['PER_OFFICE_ROUTES'][from_office]
                    )
            else:
                user_office_routes = self.config['COMPREHENSIVE_OFFICE_ROUTES']
        else:
            # I don't know how we got here, but let's assume remote.
            user_office_routes = self.config['COMPREHENSIVE_OFFICE_ROUTES']
        return user_office_routes

    def build_user_routes(self, user_string, from_office):
        """
            This is the main function of the class, and builds out the
            routes we want to have available for a user, situationally
            modified for when they're in/out of the offices.

            returns a list of IPNetwork objects.
        """
        iam_searcher = iamvpnlibrary.IAMVPNLibrary()
        # Get the user's ACLs:
        user_acl_strings = iam_searcher.get_allowed_vpn_ips(user_string)
        if not user_acl_strings:
            # If the user has NO acls, get out now.  We're probably in
            # a bad case where someone doesn't exist, or we've had an
            # upstream failure.  In any case, don't give any routes,
            # so as to provide the least privilege.
            return []
        #
        # user_acls is ['10.0.0.0/8', '192.168.50.0/24', ...]
        # a list of CIDR strings.  Since we're going to do a lot
        # of manipulation, we're going to turn these into
        # IPNetwork objects right off the bat.
        user_acls = [IPNetwork(aclstring) for aclstring in user_acl_strings]

        # First thing, take away "the routes we give everyone".
        # The user is going to get a universal route that is bigger
        # than certain pieces of their config'ed ACLs, so, let's
        # remove those from consideration for a moment.  The user will get
        # these routes back later, so this is just some housekeeping to
        # shrink the size of user_acls.
        user_acls = self.route_subtraction(
            user_acls, self.config['FREE_ROUTES'])
        #
        # Next, we are going to strip out ALL the office routes from
        # the user's ACL list.  The reason here is, their personal _ACLs_
        # are not the same as their situational _routes_.  They may have
        # an ACL to go to a certain box, but if they're in the same office,
        # we don't want them to have a ROUTE to it.  We will give them routes,
        # below, specific to how they're connecting to the VPN.  What we
        # DON'T want is a sysadmin with a big ACL coming along and having
        # that ACL dominating their routes later in this script while they're
        # in an office.
        user_acls = self.route_subtraction(
            user_acls, self.config['COMPREHENSIVE_OFFICE_ROUTES'])
        #
        # Having cleaned out, what is left is the things that a user has
        # an ACL to, that they need a ROUTE to.  So, rename it:
        user_specific_routes = user_acls

        # Now, bundle up the routes:
        # routes everyone gets, plus your personal routes...
        user_nonoffice_routes = sorted(
            cidr_merge(self.config['FREE_ROUTES'] + user_specific_routes))
        # ... plus your office routes, as calculated ...
        user_office_routes = self.get_office_routes(from_office)
        # ... equals ...
        all_routes = sorted(user_nonoffice_routes + user_office_routes)
        # Notice here, we do NOT cidr_merge at this final point.
        # The reason for this is, the user_office_routes are historically
        # a key separate route that people quickly eyeball for
        # presence/absence when triaging issues.
        #
        # If you cidr merge here, you CAN end up with something like
        # (10.X/9) instead of (10.X/10 and 10.Y/10), and if everyone is looking
        # for the Y, it can lead to false triage issues.
        #
        # In the future, this may bear reworking to move cidr_merge later in
        # the process, but we're not there yet.
        return all_routes
