#!/usr/bin/env python

import re
from dput import __appname__
from setuptools import setup

long_description = open('README.md').read()
cur = open('debian/changelog', 'r').readline().strip()
pobj = re.findall(
    r'(?P<src>.*) \((?P<version>.*)\) (?P<suite>.*); .*',
    cur
)[0]
src, version, suite = pobj
# Yes, I'm sorry, world. I'm sorry.

setup(
    name=__appname__,
    version=version,
    packages=[
        'dput',
        'dput.hooks',
        'dput.configs',
        'dput.commands',
        'dput.uploaders',
        'dput.interfaces',
    ],
    author="dput authors",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='dput-ng -- like dput, but better',
    license="GPL-2+",
    url="",
    platforms=['any']
)
