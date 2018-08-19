#!/usr/bin/python
""" Test suite for the utils library """
import unittest
import sys
from netaddr import IPNetwork
sys.path.insert(1, 'iamvpnlibrary')
# prepend the iam library so that we can locally test.
import get_user_routes  # pylint: disable=wrong-import-position
# We import our interesting library last, after modifying the
# search order, so we pick up the local copy + libraries,
# rather than ones that might be already installed.


class TestGetUserRoutes(unittest.TestCase):
    """ Class of tests """

    def setUp(self):
        """ Preparing test rig """
        self.library = get_user_routes.GetUserRoutes()

    def test_init(self):
        """ Verify that the self object was initialized """
        self.assertIsInstance(self.library,
                              get_user_routes.GetUserRoutes)
        self.assertIsNotNone(self.library.config)
        self.assertIsInstance(self.library.config, dict)
        self.assertIn('FREE_ROUTES', self.library.config)
        self.assertIn('COMPREHENSIVE_OFFICE_ROUTES', self.library.config)
        self.assertIn('PER_OFFICE_ROUTES', self.library.config)

    def test_get_office_routes_classic(self):
        """
            verify what kind of data we get for an office routes query
            the contents of the data are hard to test.  Presently this
            is 'either or' but this will change later.
            The most simple test is "when you're in the office, you have
            fewer hosts available than when you're remote"
        """
        ret1 = self.library.get_office_routes(True)
        ret2 = self.library.get_office_routes(False)
        numhosts1 = sum([x.size for x in ret1])
        numhosts2 = sum([x.size for x in ret2])
        self.assertGreater(numhosts2, numhosts1)

    def test_get_office_routes(self):
        """
            verify what kind of data we get for an office routes query
            the contents of the data are hard to test.  Presently this
            is 'either or' but this will change later.
            The most simple test is "when you're in the office, you have
            fewer hosts available than when you're remote"
        """
        ret1 = self.library.get_office_routes('sfo1')
        ret2 = self.library.get_office_routes(None)
        numhosts1 = sum([x.size for x in ret1])
        numhosts2 = sum([x.size for x in ret2])
        self.assertGreater(numhosts2, numhosts1)

    def test_route_subtraction(self):
        """
            This is a listwise removal of routes from a list of routes.
            There could be multiple cases here, but a simple smoke test
            probably covers the intent.
        """
        _input = [
            IPNetwork('10.245.0.1/24'),
            IPNetwork('10.0.0.0/8')
        ]
        office_routes = [
            IPNetwork('10.245.0.0/21'),
            IPNetwork('10.246.0.0/21')
        ]
        proper_output = [
            IPNetwork('10.0.0.0/8'),
        ]
        ret = self.library.route_subtraction(_input, office_routes)
        self.assertEqual(proper_output, ret)

    def test_route_exclusion_single(self):
        """
            This is strips part of a network out of another.
        """
        _input = [
            IPNetwork('10.50.0.0/24'),
            IPNetwork('10.51.0.0/24'),
            IPNetwork('10.52.0.0/24'),
        ]
        remove_routes = IPNetwork('10.50.0.0/25')
        proper_output = [
            IPNetwork('10.50.0.128/25'),
            IPNetwork('10.51.0.0/24'),
            IPNetwork('10.52.0.0/24'),
        ]

        ret = self.library.route_exclusion(_input, remove_routes)
        self.assertEqual(proper_output, ret)

    def test_route_exclusion_list(self):
        """
            This is strips part of a network out of another.
            There could be multiple cases here, but a simple smoke test
            probably covers the intent.
        """
        _input = [
            IPNetwork('10.50.0.0/24'),
            IPNetwork('10.51.0.0/24'),
            IPNetwork('10.52.0.0/24')
        ]
        remove_routes = [
            IPNetwork('10.50.0.0/28'),
            IPNetwork('10.51.0.128/25'),
        ]
        proper_output = [
            IPNetwork('10.50.0.16/28'),
            IPNetwork('10.50.0.32/27'),
            IPNetwork('10.50.0.64/26'),
            IPNetwork('10.50.0.128/25'),
            IPNetwork('10.51.0.0/25'),
            IPNetwork('10.52.0.0/24'),
        ]

        ret = self.library.route_exclusion(_input, remove_routes)
        self.assertEqual(proper_output, ret)

    def test_build_user_routes_bad(self):
        """
            This is failed-user test.
        """
        if not self.library.configfile.has_section('testing'):
            unittest.skip('No testing section defined')
        if not self.library.configfile.has_option('testing', 'bad_user'):
            unittest.skip('No testing/bad_user defined')
        bad_user = self.library.configfile.get('testing', 'bad_user')
        ret = self.library.build_user_routes(bad_user, True)
        self.assertEqual(ret, [])
        ret = self.library.build_user_routes(bad_user, False)
        self.assertEqual(ret, [])

    def test_build_user_routes_classic(self):
        """
            This is pretty much the "get me someone's routes" test.
            Since we're livetesting against a human, who could change their
            available routes, we can't do an awesome check.  But we can
            look for structure.
        """
        if not self.library.configfile.has_section('testing'):
            unittest.skip('No testing section defined')
        if not self.library.configfile.has_option('testing', 'normal_user'):
            unittest.skip('No testing/normal_user defined')
        normal_user = self.library.configfile.get('testing', 'normal_user')
        ret = self.library.build_user_routes(normal_user, True)
        self.assertIsInstance(ret, list)
        self.assertIsInstance(ret[0], IPNetwork)
        self.assertGreaterEqual(len(ret),
                                len(self.library.config['FREE_ROUTES']))
        ret = self.library.build_user_routes(normal_user, False)
        self.assertIsInstance(ret, list)
        self.assertIsInstance(ret[0], IPNetwork)
        _allofficeroutes = self.library.config['COMPREHENSIVE_OFFICE_ROUTES']
        _overlap_routes = (set(ret) &
                           set(_allofficeroutes))
        self.assertEqual(sorted(_overlap_routes),
                         sorted(_allofficeroutes))

    def test_build_user_routes(self):
        """
            This is pretty much the "get me someone's routes" test.
            Since we're livetesting against a human, who could change their
            available routes, we can't do an awesome check.  But we can
            look for structure.
        """
        if not self.library.configfile.has_section('testing'):
            unittest.skip('No testing section defined')
        if not self.library.configfile.has_option('testing', 'normal_user'):
            unittest.skip('No testing/normal_user defined')
        normal_user = self.library.configfile.get('testing', 'normal_user')
        # If they're in the office, they should have more routes above the
        # minimum provided by 'free'
        ret = self.library.build_user_routes(normal_user, 'sfo1')
        self.assertIsInstance(ret, list)
        self.assertIsInstance(ret[0], IPNetwork)
        self.assertGreaterEqual(len(ret),
                                len(self.library.config['FREE_ROUTES']))
        # If they're out of the office, they should have the office route.
        ret = self.library.build_user_routes(normal_user, None)
        self.assertIsInstance(ret, list)
        self.assertIsInstance(ret[0], IPNetwork)
        _allofficeroutes = self.library.config['COMPREHENSIVE_OFFICE_ROUTES']
        _overlap_routes = (set(ret) &
                           set(_allofficeroutes))
        self.assertEqual(sorted(_overlap_routes),
                         sorted(_allofficeroutes))
