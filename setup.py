#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

name = 'get_user_routes'

setup(
    name=name,
    version='1.0.1',
    author="Justin Dow",
    author_email="jdow@mozilla.com",
    url="https://github.com/jdow/get_user_routes",
    description="Calculates minimal user routes, given ACLs in LDAP",
    long_description=open('README.md').read(),
    license="MPL",
    install_requires=['libnfldap', 'netaddr'],
    py_modules=[name+'_utils'],
    scripts=[name+'.py'],
)
