#!/usr/bin/env python
""" Setup script """

import os
import subprocess
from setuptools import setup

NAME = 'get_user_routes'
VERSION = '1.0.6'


def git_version():
    """ Return the git revision as a string """
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for envvar in ['SYSTEMROOT', 'PATH']:
            val = os.environ.get(envvar)
            if val is not None:
                env[envvar] = val
        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'
        out = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               env=env).communicate()[0]
        return out

    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        git_revision = out.strip().decode('ascii')
    except OSError:
        git_revision = u"Unknown"

    return git_revision

setup(
    name='get-user-routes',
    version=VERSION,
    author="Greg Cox",
    author_email="gcox@mozilla.com",
    url="https://github.com/mozilla-it/get_user_routes",
    description=("Calculates minimal user routes, given a user's VPN ACLs\n" +
                 'This package is built upon commit ' + git_version()),
    long_description=open('README.md').read(),
    license="MPL",
    install_requires=['iamvpnlibrary>=0.8.2', 'netaddr'],
    scripts=['get-user-routes.py'],
    py_modules=[NAME],
)
