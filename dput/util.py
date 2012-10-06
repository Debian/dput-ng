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
import shutil
import importlib
import subprocess

import dput.core
from dput.core import logger
from dput.exceptions import NoSuchConfigError


def load_obj(obj_path):  # XXX: Name sucks.
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


def run_command(command):
    """
    Run a synchronized command. The argument must be a list of arguments.
    Returns a triple (stdout, stderr, exit_status)

    If there was a problem to start the supplied command, (None, None, -1) is
    returned
    """

    assert(isinstance(command, list))
    try:
        pipe = subprocess.Popen(command,
                            shell=False, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    except OSError as e:
        logger.error("Could not execute %s: %s" % (" ".join(command), e))
        return (None, None, -1)
    (output, stderr) = pipe.communicate()
    #if pipe.returncode != 0:
    #   error("Command %s returned failure: %s" % (" ".join(command), stderr))
    return (output, stderr, pipe.returncode)


def load_config(config_class, config_name, default=None):  # XXX: Name sucks,
#                                                                 try again.
    """
    Load a config by abstract name. Interally, this searches the
    `dput.core.CONFIG_LOCATIONS` for a subfolder (with the name of
    config_class) with a file by the name of `config_name`.json. If it finds
    it, it returns the object representation of the JSON file.

    If there is no such file, this will throw a
    `dput.exceptions.NoSuchConfigError`.
    """

    master = {}
    if config_name != 'DEFAULT':
        # we should fetch the master
        logger.debug("Loading the DEFAULT configurator for this class.")
        master = load_config(config_class, 'DEFAULT', default={})

    logger.debug("Loading config: %s %s" % (config_class,
                                            config_name))
    ret = {}
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
            ret.update(json.load(open(path, 'r')))

    if ret != {}:
        master.update(ret)
        return master

    if default is not None:
        return default
    elif master != {}:
        return master

    logger.debug("Failed to load config.")

    nsce = NoSuchConfigError("No such config: '%s' in class '%s'" % (
        config_name,
        config_class
    ))

    nsce.config_class = config_class
    nsce.config_name = config_name
    nsce.checked = dput.core.CONFIG_LOCATIONS
    raise nsce
