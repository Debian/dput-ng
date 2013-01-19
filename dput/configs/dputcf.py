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
Old dput config file implementation
"""

import os
import sys

if sys.version_info[0] >= 3:
    import configparser
else:
    import ConfigParser as configparser

import dput.core
from dput.config import AbstractConfig
from dput.core import logger
from dput.exceptions import DputConfigurationError


class DputCfConfig(AbstractConfig):
    """
    dput-old config file implementation. Subclass of a
    :class:`dput.config.AbstractConfig`.
    """

    def preload(self, configs):
        """
        See :meth:`dput.config.AbstractConfig.preload`
        """
        parser = configparser.ConfigParser()
        if configs is None:
            configs = dput.core.DPUT_CONFIG_LOCATIONS

        for config in configs:
            if not os.access(config, os.R_OK):
                logger.debug("Skipping file %s: Not accessible" % (
                    config
                ))
                continue
            try:
                logger.trace("Parsing %s" % (config))
                parser.readfp(open(config, 'r'))
            except IOError as e:
                logger.warning("Skipping file %s: %s" % (
                    config,
                    e
                ))
                continue
            except configparser.ParsingError as e:
                raise DputConfigurationError("Error parsing file %s: %s" % (
                    config,
                    e
                ))
        self.parser = parser
        self.configs = configs
        self.defaults = self._translate_strs(self.get_config("DEFAULT"))
        self.parser.remove_section("DEFAULT")

    def set_replacements(self, replacements):
        """
        See :meth:`dput.config.AbstractConfig.set_replacements`
        """
        for replacement in replacements:
            if self.parser.has_section(replacement):
                self.parser.set(replacement,
                                replacement,
                                replacements[replacement])

    def get_config_blocks(self):
        """
        See :meth:`dput.config.AbstractConfig.get_config_blocks`
        """
        return self.parser.sections()

    def get_defaults(self):
        """
        See :meth:`dput.config.AbstractConfig.get_defaults`
        """
        return self.defaults

    def _translate_strs(self, ret):
        trans = {
            "1": True,
            "0": False
        }
        ret = self._translate_dict(ret, trans)
        return ret

    def _translate_bools(self, ret):
        trans = {
            True: "1",
            False: "0"
        }
        return self._translate_dict(ret, trans)

    def _translate_dict(self, ret, trans):
        if isinstance(ret, dict):
            ret = ret.copy()
        elif isinstance(ret, list):
            ret = ret[:]

        for key in ret:
            val = ret[key]
            if isinstance(val, dict) or isinstance(val, list):
                ret[key] = self._translate_dict(val, trans)
                continue

            if val in trans:
                val = trans[val]
                ret[key] = val
        return ret

    def get_config(self, name):
        """
        See :meth:`dput.config.AbstractConfig.get_config`
        """
        ret = {}
        try:
            items = self.parser.items(name)
        except configparser.NoSectionError:
            return {}
        for key, val in items:
            ret[key] = val
        ret['name'] = name
        ret = self._translate_strs(ret)
        return ret
