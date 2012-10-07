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
from dput.util import get_obj
from dput.exceptions import DputConfigurationError


def run_checker(checker, changes, dput_config, profile):
    logger.debug("running checker: %s" % (checker))
    obj = get_obj('checkers', checker)
    if obj is None:
        raise DputConfigurationError("No such checker: `%s'" % (
            interface
        ))

    interface = 'cli'
    if 'interface' in profile:
        interface = profile['interface']
    logger.debug("Using interface %s" % (interface))
    interface = get_obj('interfaces', interface)
    if interface is None:
        raise DputConfigurationError("No such interface: `%s'" % (
            interface
        ))
    interface = interface()
    interface.initialize()

    ret = obj(
        changes,
        dput_config,
        profile,
        interface
    )

    interface.shutdown()
    return ret
