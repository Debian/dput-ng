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


import dput.conf
import dput.util
from dput.exceptions import DputConfigurationError


def load_profile(profile_name):

    repls = {}
    if profile_name and ":" in profile_name:
        profile_name, arg = profile_name.split(":", 1)
        repls[profile_name] = arg

    profile = dput.util.load_config(
        'profiles',
        profile_name,
        default={}
    )
    for thing in profile:
        if thing in repls:
            val = profile[thing]
            val = val.replace("%(%s)s" % (thing), repls[thing])
            profile[thing] = val

    try:
        conf = dput.conf.load_dput_configs(profile_name, repls)
        for key in conf._data:
            profile[key] = conf._data[key]  # XXX: GAHHHH, MY EYES ಥ_ಥ
        profile['name'] = conf.name()
    except DputConfigurationError:
        if 'fqdn' in profile:
            profile['name'] = profile_name

    return profile
