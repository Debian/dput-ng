#!/usr/bin/env python

from dput import __appname__, __version__
from setuptools import setup

long_description = open('README.md').read()

setup(
    name=__appname__,
    version=__version__,
    packages=[
        'dput',
        'dput.checkers',
        'dput.uploaders'
    ],
    author="dput authors",
    author_email="paultag@debian.org",
    long_description=long_description,
    description='dput-ng -- like dput, but better',
    license="GPL-2+",
    url="",
    platforms=['any']
)
