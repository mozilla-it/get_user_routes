#!/usr/bin/python
import unittest
from lib.helper import cidr_to_netmask, squash_routes, remove_office_routes


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

