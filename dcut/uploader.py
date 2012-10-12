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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import abc
import os

import dput.profile
from dput.exceptions import UploadException, DputConfigurationError
from dput.core import (CONFIG_LOCATIONS, logger)
from dput.util import get_obj

class AbstractCommand(object):
    """
    Abstract base class for all concrete dcut command implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, profile):
        self._config = profile

    @abc.abstractmethod
    def register(self, **kwargs):
        pass

    @abc.abstractmethod
    def produce(self, filename):
        pass

    @abc.abstractmethod
    def validate(self, **kwargs):
        pass


def find_commands():
    profiles = set()
    logger.trace("Profiles: %s" % (str(profiles)))
    for path in CONFIG_LOCATIONS:
        path = "%s/commands" % (path)
        if os.path.exists(path):
            for fil in os.listdir(path):
                xtn = ".json"
                if fil.endswith(xtn):
                    profiles.add(fil[:-len(xtn)])
    return profiles

def load_commands():
    for command in find_commands():
        logger.debug("importing command: %s" % (command))
        obj = get_obj('commands', command)
        if obj is None:
            raise DputConfigurationError("No such checker: `%s'" % (
                command
            ))
        print(obj)

def invoke_dcut(args):
    profile = dput.profile.load_profile(args.host)

    fqdn = None
    if 'fqdn' in profile:
        fqdn = profile['fqdn']

    if not 'allow_dcut' in profile or not profile['allow_dcut']:
        raise UploadException("Profile %s does not allow command file uploads"
                              "Please set allow_dcut=1 to allow such uploads")

    logger.info("Uploading commands file to %s (incoming: %s)" % (
        fqdn or profile['name'],
        profile['incoming']
    ))

    print(profile)
    print(load_commands())
