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

import abc


def load_configs(replacements):
    from dput.configs.dputcf import DputCfConfig
    from dput.configs.dputng import DputProfileConfig

    configs = [DputProfileConfig(replacements), DputCfConfig(replacements)]
    defaults = {}

    for config in configs:
        defaults.update(config.get_defaults())

    for config in configs:
        config.set_defaults(defaults)

    return configs


class AbstractConfig(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, replacements):
        self.preload(replacements)

    @abc.abstractmethod
    def set_defaults(self, defaults):
        pass

    @abc.abstractmethod
    def get_defaults(self):
        pass

    @abc.abstractmethod
    def get_config(self, name):
        pass

    @abc.abstractmethod
    def get_config_blocks(self):
        pass

    @abc.abstractmethod
    def preload(self):
        pass
