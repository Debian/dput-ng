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
import json
import importlib

import dput.core
from dput.core import logger
from dput.exceptions import NoSuchConfigError


def load_obj(obj_path):
    """
    Dynamically load an object (class, method, etc) by name (such as
    `dput.core.ClassName`), and return that object to work with. This is
    useful for loading modules on the fly, without them being all loaded at
    once, or even in the same package.

    Call this routine with at least one dot in it -- it attempts to load the
    module (such as dput.core) and use getattr to load the thing - similar to
    how `from` works.
    """
    logger.debug("Loading object: %s" % (obj_path))
    module, obj = obj_path.rsplit(".", 1)
    mod = importlib.import_module(module)
    fltr = getattr(mod, obj)
    return fltr


def load_config(config_class, config_name):
    """
    Load a config by abstract name. Interally, this searches the
    `dput.core.CONFIG_LOCATIONS` for a subfolder (with the name of
    config_class) with a file by the name of `config_name`.json. If it finds
    it, it returns the object representation of the JSON file.

    If there is no such file, this will throw a
    `dput.exceptions.NoSuchConfigError`.
    """
    logger.debug("Loading config: %s %s" % (config_class,
                                            config_name))
    template_path = "%s/%s/%s.json"
    for config in dput.core.CONFIG_LOCATIONS:
        logger.debug("Checking for config: %s" % (config))
        path = template_path % (
            config,
            config_class,
            config_name
        )
        logger.debug("Checking - %s" % (path))
        if os.path.exists(path):
            logger.debug("Loaded config.")
            return json.load(open(path, 'r'))

    logger.debug("Failed to load config.")

    nsce = NoSuchConfigError("No such config: '%s' in class '%s'" % (
        config_name,
        config_class
    ))

    nsce.config_class = config_class
    nsce.config_name = config_name
    nsce.checked = dput.core.CONFIG_LOCATIONS
    raise nsce


def load_dput_config(config_file, base_config=None):
    """
    Process and load a dput ini-style config file.
    Remember to set your defaults later, kids
    """
    logger.debug("Loading dput config - %s" % (config_file))

    segment = None
    ret = {None: {}}  # catchall for malformated files.
    if base_config:
        ret.update(base_config)

    for line in open(config_file, 'r').readlines():
        line = line.strip()
        if line == '' or line[0] == '#':
            continue  # don't bother with comments at all, or blank lines.

        if line[0] == '[' and line[len(line) - 1] == ']':  # segment
            segment = line[1:-1]
            ret[segment] = {}
            continue

        key, value = [x.strip() for x in line.split("=", 1)]  # key/val line
        ret[segment][key] = value

    ret.pop(None)  # pop the catchall off
    return ret


def load_dput_configs():
    """
    Load all the dput config files to take action in a sane way. Internally,
    this checks for each file `dput.core.DPUT_CONFIG_LOCATIONS`, and if found,
    attempts to parse the key/value pairs. Each subsequent file may override
    the last.

    Special-cased handling on the blocked labeled "DEFAULT" allows that to
    serve as an underlay for missing keys.
    """
    logger.debug("Loading dput configs")
    ret = {}
    for config in dput.core.DPUT_CONFIG_LOCATIONS:
        if os.path.exists(config):
            ret = load_dput_config(config, base_config=ret)
    ret = set_dput_config_defaults(ret)
    return ret


def set_dput_config_defaults(ret):
    """
    Pop the `DEFAULT` key off the dict and use it to set any unset keys.

    Should be called on objects returned by `load_dput_config` at some point.
    """
    if "DEFAULT" in ret:
        logger.debug("        dput config - setting DEFAULTs")
        ddict = ret.pop("DEFAULT")
        for key in ddict:  # for each default
            for segment in ret:  # go over every other block
                if not key in ret[segment]:  # and set the val if its not there
                    ret[segment][key] = ddict[key]
    return ret
