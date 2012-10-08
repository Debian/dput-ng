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

import os

from dput.util import load_config
from dput.core import (CONFIG_LOCATIONS, logger)
from dput.config import AbstractConfig
from dput.exceptions import DputConfigurationError


def get_sections():
    profiles = set()
    logger.debug("Profiles: %s" % (str(profiles)))
    for path in CONFIG_LOCATIONS:
        path = "%s/profiles" % (path)
        if os.path.exists(path):
            for fil in os.listdir(path):
                xtn = ".json"
                if fil.endswith(xtn):
                    profiles.add(fil[:-len(xtn)])
    return profiles


class DputProfileConfig(AbstractConfig):
    def preload(self, replacements):
        self.configs = {}
        self.replacements = replacements
        for section in get_sections():
            self.configs[section] = self.load_config(section)

    def get_config_blocks(self):
        return self.configs.keys()

    def get_defaults(self):
        return self.configs['DEFAULT']

    def set_defaults(self, defaults):
        self.configs['DEFAULT'] = defaults

    def get_config(self, name):
        logger.debug("Getting %s" % (name))
        default = self.configs['DEFAULT'].copy()
        if name in self.configs:
            default.update(self.configs[name])
            default['name'] = name
            for key in default:
                val = default[key]
                if "%(" in val and ")s" in val:
                    logger.debug("error with %s -> %s" % (
                        key,
                        val
                    ))
                    raise DputConfigurationError(
                        "Unconverted values in key `%s' - %s" % (
                            key,
                            val
                        )
                    )
            return default
        return {}

    def load_config(self, name):
        profile = load_config(
            'profiles',
            name,
            default={}
        )
        repls = self.replacements
        for thing in profile:
            val = profile[thing]
            if not isinstance(val, basestring):
                continue
            for repl in repls:
                if repl in val:
                    val = val.replace("%%(%s)s" % (repl), repls[repl])
            profile[thing] = val
        return profile
