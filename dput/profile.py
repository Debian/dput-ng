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
import dput.core
import dput.conf
import dput.util
from dput.conf import load_configuration
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
        val = profile[thing]
        if not isinstance(val, basestring):
            continue
        for repl in repls:
            if repl in val:
                val = val.replace("%%(%s)s" % (repl), repls[repl])
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


def get_sections():
    cf = load_configuration(dput.core.DPUT_CONFIG_LOCATIONS, {})
    profiles = set(cf.sections())
    for path in dput.core.CONFIG_LOCATIONS:
        path = "%s/profiles" % (path)
        if os.path.exists(path):
            for fil in os.listdir(path):
                xtn = ".json"
                if fil.endswith(xtn):
                    profiles.add(fil[:-len(xtn)])
    return profiles


def profiles():
    profiles = get_sections()
    for profile in profiles:
        yield load_profile(profile)
