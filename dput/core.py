# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2012 dput authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""
.. module:: dput.core
    :synopsis: core objects & data structures

Stuff that everything uses and shouldn't keep pulling on their own.
"""

import os.path
import logging


# used for searching for config files. place in order of precedence
CONFIG_LOCATIONS = [
    "/usr/share/dput-ng/",
    "/etc/dput.d/",
    os.path.expanduser("~/.dput.d"),
    "skel/",
]
"""
Locations to look for JSON-ey config files. Under each directory may exist
a ``class``, which is a folder full of json files, which may be loaded.
The order dicates which has the most precedence.
"""

DPUT_CONFIG_LOCATIONS = [
    "/etc/dput.cf",
    os.path.expanduser("~/.dput.cf")
]
"""
Locations to look for old-style dput.cf configuration files.
"""

# logging routines.
logger = logging.getLogger("dput")
"""
Logger, for general output and stuff.
"""

logger.setLevel(logging.DEBUG)

# basic config
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_formatter = logging.Formatter(
    '%(levelname)s %(funcName)s: %(message)s')
_ch.setFormatter(_formatter)

logger.addHandler(_ch)
