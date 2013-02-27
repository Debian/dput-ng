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
Stuff that everything uses and shouldn't keep pulling on their own.
"""

import sys
import os.path
import logging
import traceback
import getpass

import dput.logger
from logging.handlers import RotatingFileHandler


# used for searching for config files. place in order of precedence
CONFIG_LOCATIONS = {
    "/usr/share/dput-ng/": 30,
    "/etc/dput.d/": 20,
    os.path.expanduser("~/.dput.d"): 10,
    "skel/": 100
}
"""
Locations to look for JSON-ey config files. Under each directory may exist
a ``class``, which is a folder full of json files, which may be loaded.
The order dicates which has the most precedence.
"""

DPUT_CONFIG_LOCATIONS = {
    "/etc/dput.cf": 15,
    os.path.expanduser("~/.dput.cf"): 5
}
"""
Locations to look for old-style dput.cf configuration files.
"""

SCHEMA_DIRS = [
    "/usr/share/dput-ng/schemas",
    "skel/schemas"
]
"""
validictory schemas
"""

# logging routines
logging.setLoggerClass(dput.logger.DputLogger)
logger = logging.getLogger("dput")
"""
Logger, for general output and stuff.
"""

logger.setLevel(dput.logger.TRACE)

# basic config
_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_formatter = logging.Formatter(
    '%(message)s')
_ch.setFormatter(_formatter)


def _write_upload_log(logfile, full_log):
    upload_log_formatter = logging.Formatter(
        "%(asctime)s - dput[%(process)d]: "
        "%(module)s.%(funcName)s - %(message)s"
    )
    upload_log_handler = RotatingFileHandler(logfile)
    upload_log_handler.setFormatter(upload_log_formatter)
    if full_log:
        upload_log_handler.setLevel(logging.DEBUG)
    else:
        upload_log_handler.setLevel(logging.INFO)
    logger.addHandler(upload_log_handler)


def _enable_debugging(level):
    _ch = logging.StreamHandler()
    if level == 1:
        _ch.setLevel(logging.DEBUG)
    if level >= 2:
        _ch.setLevel(dput.logger.TRACE)
    _formatter = logging.Formatter(
        '[%(levelname)s] %(created)f: (%(funcName)s) %(message)s')
    _ch.setFormatter(_formatter)
    logger.addHandler(_ch)

logger.addHandler(_ch)


def mangle_sys():
    for root in CONFIG_LOCATIONS:
        pth = "%s/scripts" % (root)
        pth = os.path.abspath(pth)
        if pth not in sys.path:
            logger.debug("Loading external script location %s" % (pth))
            sys.path.insert(0, pth)


def maybe_print_traceback(debug_level, stack):
    if debug_level > 1:
        tb = traceback.format_tb(stack[2])
        logger.trace("Traceback:")
        for level in tb:
            for tier in level.split("\n"):
                logger.trace(tier)

def get_local_username():
    try:
        local_user = getpass.getuser()
    except Exception as e:
        logger.warn("Could not determine local username: %s" % e)
        local_user = None
    return local_user
