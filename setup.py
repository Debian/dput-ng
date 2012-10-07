#!/usr/bin/env python

import subprocess
from dput import __appname__
from setuptools import setup

long_description = open('README.md').read()

v_cmd = "dpkg-parsechangelog | grep '^Version' | sed 's/.*: //g'"  # Hack
version = subprocess.check_output(["sh", "-c", v_cmd]).strip()
# XXX: This hack above is bad, mmkay? Please don't use this widly.
#      we just really need to tie the version to the package module.

setup(
    name=__appname__,
    version=version,
    packages=[
        'dput',
        'dput.checkers',
        'dput.uploaders',
        'dput.interfaces'
    ],
    author="dput authors",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='dput-ng -- like dput, but better',
    license="GPL-2+",
    url="",
    platforms=['any']
)
