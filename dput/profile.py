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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""
Profile implementation & routines. This handles all external access
of the Profile data.
"""

import logging
import re
import shlex

import dput.core
from dput.core import logger
from dput.config import AbstractConfig
from dput.configs.dputcf import DputCfConfig
from dput.configs.dputng import DputProfileConfig
from dput.exceptions import DputConfigurationError
from dput.util import _config_cleanup, validate_object


classes = {
    "dputng": DputProfileConfig,
    "dputcf": DputCfConfig
}


def _blame_map(obj, blame):
    ret = {}
    for key in obj:
        val = obj[key]
        if isinstance(val, dict):
            ret[key] = _blame_map(obj[key], blame)
        if isinstance(val, list):
            vals = {}
            for v in val:
                vals[v] = blame
            ret[key] = vals
        else:
            ret[key] = blame
    return ret


class MultiConfig(AbstractConfig):
    """
    Multi-configuration abstraction. This helps abstract
    the underlying configurations from the user.

    This is a subclass of :class:`dput.config.AbstractConfig`
    """

    def __init__(self):
        configs = []
        for config in dput.core.CONFIG_LOCATIONS:
            configs.append({
                "type": "dputng",
                "loc": config,
                "weight": dput.core.CONFIG_LOCATIONS[config]
            })
        for config in dput.core.DPUT_CONFIG_LOCATIONS:
            configs.append({
                "type": "dputcf",
                "loc": config,
                "weight": dput.core.DPUT_CONFIG_LOCATIONS[config]
            })

        configs = sorted(configs, key=lambda c: c['weight'])
        configs.reverse()
        self.preload(configs)

    def set_replacements(self, replacements):
        """
        See :meth:`dput.config.AbstractConfig.set_replacements`
        """
        for config in self.configs:
            config.set_replacements(replacements)

    def preload(self, objs):
        """
        See :meth:`dput.config.AbstractConfig.preload`
        """
        configs = []
        for obj in objs:
            configs.append(
                classes[obj['type']](
                    [obj['loc']]
                )
            )

        self.configs = configs

        defaults_blame = {}
        defaults = {}

        for config in configs:
            defaults.update(config.get_defaults())
            defaults = _config_cleanup(defaults)
            defaults_blame.update(
                _blame_map(config.get_defaults(), "%s (%s)" % (
                    config.path,
                    'DEFAULT'
                ))
            )

        self.defaults = defaults
        self.defaults_blame = defaults_blame

    def get_defaults(self):
        """
        See :meth:`dput.config.AbstractConfig.get_defaults`
        """
        return self.get_config("DEFAULT")

    def get_config(self, name):
        """
        See :meth:`dput.config.AbstractConfig.get_config`
        """
        logger.trace("Loading entry %s" % (name))
        ret = self.defaults.copy()
        for config in self.configs:
            obj = config.get_config(name)
            logger.trace(obj)
            ret.update(obj)
            ret = _config_cleanup(ret)
            logger.trace('Rewrote to:')
            logger.trace(obj)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Got configuration: %s" % (name))
            for key in ret:
                logger.debug("\t%s: %s" % (key, ret[key]))

        validate_object('config', ret, 'profiles/%s' % (name))
        return ret

    def get_blame(self, name):
        ret = self.defaults_blame
        for config in self.configs:
            obj = config.get_config(name)
            ret.update(_blame_map(obj, "%s (%s)" % (
                config.path,
                name
            )))
        return ret

    def get_config_blocks(self):
        """
        See :meth:`dput.config.AbstractConfig.get_config_blocks`
        """
        ret = set()
        for config in self.configs:
            for block in config.get_config_blocks():
                ret.add(block)
        if "DEFAULT" in ret:
            ret.remove("DEFAULT")
        return ret


_multi_config = None


def load_profile(host):
    """
    Load a profile, for a given host ``host``. In the case where
    ``host`` has a ":", that'll be treated as an expansion for
    config strings. For instance:

    ``ppa:paultag/fluxbox`` will expand any ``%(ppa)s`` strings to
    ``paultag/fluxbox``. Comes in super handy.
    """
    global _multi_config

    repls = {}
    if host and ":" in host:
        host, arg = host.split(":", 1)
        repls[host] = arg

    if _multi_config is None:
        _multi_config = MultiConfig()
    config = _multi_config
    config.set_replacements(repls)
    configs = config.get_config_blocks()

    if host in configs:
        return config.get_config(host)

    if host is not None:
        raise DputConfigurationError("Error, was given host, "
                                     "but we don't know about it.")

    for block in configs:
        try:
            obj = config.get_config(block)
        except DputConfigurationError:
            continue  # We don't have fully converted blocks.

        if "default_host_main" in obj and \
           obj['default_host_main'] != "":
            return obj
    return config.get_config("ftp-master")


def profiles():
    """
    Get a list of all profiles we know about. It returns a set of
    strings, which can be accessed with :func:`load_profile`
    """
    global _multi_config
    if _multi_config is None:
        _multi_config = MultiConfig()
    config = _multi_config
    configs = config.get_config_blocks()
    if "DEFAULT" in configs:
        configs.remove("DEFAULT")
    return configs


def get_blame_map(name):
    global _multi_config
    if _multi_config is None:
        _multi_config = MultiConfig()
    config = _multi_config
    configs = config.get_blame(name)
    return configs


def parse_overrides(overrides):
    """
    Translate a complex string structure into a JSON like object. For example
    this function would translate foo.bar=baz like strings into objects
    overriding the JSON profile.

    Basically this function function will take any object separated by a dot on
    the left side as a dict object, whereas the terminal value on the right
    side is taken literally.
    """
    # This function involves lots of black magic.
    # Generally we expect a foo.bar=value format, with foo.bar being a profile
    # key and value being $anything.
    # However, people might provide that in weird combinations such as
    # 'foo.bar      =     "value value"'
    override_obj = {}
    for override in overrides:
        parent_obj = override_obj
        if override.find("=") > 0 or override.startswith("-") > 0:
            (profile_key, profile_value) = (None, None)
            if override.startswith("-"):
                profile_key = override[1:]
                profile_value = None
            else:
                (profile_key, profile_value) = override.split("=", 1)
                profile_value = shlex.split(profile_value)
            profile_key = re.sub('\s', '', profile_key)
            profile_key = profile_key.split(".")
            last_item = profile_key.pop()

            for key in profile_key:
                if not key in parent_obj:
                    parent_obj[key] = {}
                parent_obj = parent_obj[key]

            if isinstance(parent_obj, list):
                raise DputConfigurationError("Ambiguous override: object %s "
                    "can either be a composite type or a terminal, not both" %
                    (last_item))

            if not last_item in parent_obj:
                parent_obj[last_item] = []
            if last_item in parent_obj and not (
                                    isinstance(parent_obj[last_item], list)):
                raise DputConfigurationError("Ambiguous override: object %s "
                    "can either be a composite type or a terminal, not both" %
                    (last_item))
            parent_obj[last_item].append(profile_value)
        else:
            raise DputConfigurationError(
                           "Profile override %s does not seem to match the "
                           "expected format" % override)
    return override_obj
