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
Implementation regarding configuration files & their internal representation
to the dput profile code.
"""

import abc


class AbstractConfig(object):
    """
    Abstract Configuration Object. All concrete configuration implementations
    must subclass this object.

    Basically, all subclasses are bootstrapped in the same-ish way:

        * preload
        * get_defaults
        * set defaults
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, configs):
        self.preload(configs)
        self.path = ' '.join(configs)

    @abc.abstractmethod
    def set_replacements(self, replacements):
        """
        """
        pass  # XXX: DOCUMENT ME.

    @abc.abstractmethod
    def get_defaults(self):
        """
        Get the defaults that concrete configs get overlaid on top of. In
        theory, this is set during the bootstrapping process.
        """
        pass

    @abc.abstractmethod
    def get_config(self, name):
        """
        Get a configuration block. What this means is generally up to the
        implementation. However, please keep things sane and only return
        sensual upload target blocks.
        """
        pass

    @abc.abstractmethod
    def get_config_blocks(self):
        """
        Get a list of all configuration blocks. Strings in a list.
        """
        pass

    @abc.abstractmethod
    def preload(self, replacements):
        """
        Load all configuration blocks.
        """
        pass
