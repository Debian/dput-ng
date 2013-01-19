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
dput-ng native configuration file implementation.
"""

import sys

from dput.util import load_config, get_configs
from dput.core import logger
from dput.config import AbstractConfig
from dput.exceptions import DputConfigurationError


def get_sections():
    """
    Get all profiles we know about.
    """
    return get_configs('profiles')


if sys.version_info[0] >= 3:
    _basestr_type = str
else:
    _basestr_type = basestring


class DputProfileConfig(AbstractConfig):
    """
    dput-ng native config file implementation. Subclass of a
    :class:`dput.config.AbstractConfig`.
    """

    def preload(self, configs):
        """
        See :meth:`dput.config.AbstractConfig.preload`
        """
        self.configs = configs
        self.replacements = {}
        self.cache = {}
        self.defaults = {}
        self.defaults = self.get_config("DEFAULT")

    def set_replacements(self, replacements):
        """
        See :meth:`dput.config.AbstractConfig.set_replacements`
        """
        self.replacements = replacements

    def get_config_blocks(self):
        """
        See :meth:`dput.config.AbstractConfig.get_config_blocks`
        """
        return get_sections()

    def get_defaults(self):
        """
        See :meth:`dput.config.AbstractConfig.get_defaults`
        """
        return self.defaults.copy()

    def get_config(self, name):
        """
        See :meth:`dput.config.AbstractConfig.get_config`
        """
        kwargs = {
            "default": {}
        }

        configs = self.configs
        if configs is not None:
            kwargs['configs'] = configs

        kwargs['config_cleanup'] = False

        profile = load_config(
            'profiles',
            name,
            **kwargs
        )
        logger.trace("name: %s - %s / %s" % (name, profile, kwargs))
        repls = self.replacements
        for thing in profile:
            val = profile[thing]
            if not isinstance(val, _basestr_type):
                continue
            for repl in repls:
                if repl in val:
                    val = val.replace("%%(%s)s" % (repl), repls[repl])
            profile[thing] = val

        ret = {}
        ret.update(profile)
        ret['name'] = name

        for key in ret:
            val = ret[key]
            if isinstance(val, _basestr_type):
                if "%(" in val and ")s" in val:
                    raise DputConfigurationError(
                        "Half-converted block: %s --> %s" % (
                            key,
                            val
                        )
                    )
        return ret
