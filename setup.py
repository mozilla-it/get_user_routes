#!/usr/bin/env python

import distutils.core

name = 'get_user_routes'

distutils.core.setup(name=name,
    version='1.0',
    author="Justin Dow",
    author_email="jdow@mozilla.com",
    url="https://github.com/jdow/get_user_routes",
    description="Calculates minimal user routes, given ACLs in LDAP",
    long_description=open('README.md').read(),
    license="MPL",
    requires=['libnfldap', 'netaddr'],
    packages=['lib'],
    py_modules=[name],

#    scripts=[name],
#    data_files=[
#        ('/usr/local/bin', [name + '.py']),
#        ('/usr/local/etc', [name + '.conf']),
#        ('/usr/local/lib', [name]),
#        ('/usr/local/lib/__init__.py'),
#
#    ],
)
