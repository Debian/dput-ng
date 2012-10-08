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

from dput.core import logger
from dput.config import AbstractConfig
from dput.configs.dputcf import DputCfConfig
from dput.configs.dputng import DputProfileConfig
from dput.exceptions import DputConfigurationError

class MultiConfig(AbstractConfig):
    def preload(self, replacements):
        configs = [
            DputProfileConfig(replacements),
            DputCfConfig(replacements)
        ]
        self.configs = configs

        defaults = {}
        for config in configs:
            defaults.update(config.get_defaults())

        self.set_defaults(defaults)

    def set_defaults(self, defaults):
        logger.debug("Default set: %s" % (defaults))
        for config in self.configs:
            config.set_defaults(defaults)

    def get_defaults(self):
        return self.get_config("DEFAULT")

    def get_config(self, name):
        ret = {}
        for config in self.configs:
            obj = config.get_config(name)
            ret.update(obj)
        logger.debug("Got config %s, %s" % (name, ret))
        return ret

    def get_config_blocks(self):
        ret = set()
        for config in self.configs:
            for block in config.get_config_blocks():
                ret.add(block)
        return ret


def load_profile(host):
    repls = {}
    if host and ":" in host:
        host, arg = host.split(":", 1)
        repls[host] = arg

    config = MultiConfig(repls)
    configs = config.get_config_blocks()

    if host in configs:
        return config.get_config(host)

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
    config = MultiConfig({})
    configs = config.get_config_blocks()
    if "DEFAULT" in configs:
        configs.remove("DEFAULT")
    return configs
