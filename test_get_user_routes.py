"""
    Run with nosetests filename.py
"""

import unittest
from lib.helper import cidr_to_netmask


class TestGetUserRoutes(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_cidr_to_netmask(self):
        input = '10.0.0.0/8'
        output = ('10.0.0.0', '255.0.0.0')
        ret = cidr_to_netmask(input)
        self.assertEqual(output, ret)

