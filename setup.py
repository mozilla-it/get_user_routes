#!/usr/bin/env python
""" Setup script """

from setuptools import setup

NAME = 'get_user_routes'

setup(
    name=NAME,
    version='1.0.5',
    author="Greg Cox",
    author_email="gcox@mozilla.com",
    url="https://github.com/mozilla-it/get_user_routes",
    description="Calculates minimal user routes, given a user's VPN ACLs",
    long_description=open('README.md').read(),
    license="MPL",
    install_requires=['iamvpnlibrary>=0.8.2', 'netaddr'],
    scripts=[NAME+'.py'],
)
