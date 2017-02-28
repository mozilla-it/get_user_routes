#!/usr/bin/python
import unittest
from lib.helper import cidr_to_netmask, squash_routes, remove_office_routes, \
        ldap_routes_not_in_config, standardize_acls


class TestGetUserRoutes(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cidr_to_netmask(self):
        input = '10.0.0.0/8'
        proper_output = ('10.0.0.0', '255.0.0.0')
        ret = cidr_to_netmask(input)
        self.assertEqual(proper_output, ret)

    def test_squash_routes(self):
        input = [
            '10.0.0.0/8',
            '10.8.0.0/16',
            '63.245.1.5/32'
        ]
        proper_output = [
            '10.0.0.0/8',
            '63.245.1.5/32'
        ]
        ret = squash_routes(input)
        self.assertEqual(proper_output, ret)

    def test_squash_routes(self):
        input = [
            '10.0.0.0/8',
            '10.8.0.0/16',
            '63.245.1.5/32',
            '63.245.1.5/32'
        ]
        proper_output = [
            '10.0.0.0/8',
            '63.245.1.5/32'
        ]
        ret = squash_routes(input)
        self.assertEqual(proper_output, ret)

    def test_remove_office_routes(self):
        input = [
            '10.245.0.1/24',
            '10.0.0.0/8'
        ]
        office_routes = [
            '10.245.0.0/21',
            '10.246.0.0/21'
        ]
        proper_output = [
            '10.0.0.0/8',
        ]
        ret = remove_office_routes(input, office_routes)
        self.assertEqual(proper_output, ret)

    def test_remove_office_routes_with_unknown(self):
        input = [
            '10.245.0.1/24',
            '10.247.0.1/24',
            '10.0.0.0/8'
        ]
        office_routes = [
            '10.245.0.0/21',
            '10.246.0.0/21'
        ]
        proper_output = [
            '10.247.0.1/24',
            '10.0.0.0/8'
        ]
        ret = remove_office_routes(input, office_routes)
        self.assertEqual(proper_output, ret)

    def test_ldap_routes_not_in_config(self):
        input = [
            '10.0.0.0/8',
            '63.245.1.5'
        ]
        config_routes = [
            '10.0.0.0/8',
        ]
        proper_output = [
            '63.245.1.5'
        ]
        ret = ldap_routes_not_in_config(input, config_routes)
        self.assertEqual(proper_output, ret)

    def test_standardize_acls(self):
        input = {'vpn_admin': {'10.8.0.0/16': 'DC', '10.21.0.5': 'HOST'}, 'vpn_inventory': {'10.22.75.208:443': 'inventory-host','10.22.75.208:80': 'inventory-host'}}

        proper_output = [
                '10.22.75.208/32',
                '10.22.75.208/32',
                '10.21.0.5/32',
                '10.8.0.0/16'
            ]
        ret = standardize_acls(input)
        self.assertEqual(proper_output, ret)

