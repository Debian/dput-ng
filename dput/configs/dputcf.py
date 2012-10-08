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
import ConfigParser

from dput.config import AbstractConfig
from dput.core import (DPUT_CONFIG_LOCATIONS, logger)
from dput.exceptions import DputConfigurationError


class DputCfConfig(AbstractConfig):
    def preload(self, replacements):
        parser = ConfigParser.ConfigParser()
        for config in DPUT_CONFIG_LOCATIONS:
            if not os.access(config, os.R_OK):
                logger.warning("Skipping file %s: Not accessible" % (
                    config
                ))
                continue
            try:
                logger.debug("Parsing %s" % (config))
                parser.readfp(open(config, 'r'))
            except IOError as e:
                logger.warning("Skipping file %s: %s" % (
                    config,
                    e
                ))
                continue
            except ConfigParser.ParsingError as e:
                raise DputConfigurationError("Error parsing file %s: %s" % (
                    config,
                    e
                ))

        for replacement in replacements:
            if parser.has_section(replacement):
                parser.set(replacement, replacement, replacements[replacement])
        self.parser = parser

    def get_config_blocks(self):
        return self.parser.sections()

    def get_defaults(self):
        return self.get_config("DEFAULT")

    def set_defaults(self, defaults):
        for key in defaults:
            self.parser.set("DEFAULT", key, defaults[key])

    def get_config(self, name):
        ret = {}
        try:
            items = self.parser.items(name)
        except ConfigParser.NoSectionError:
            return {}
        for key, val in items:
            ret[key] = val
        ret['name'] = name
        return ret
