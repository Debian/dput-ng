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

# XXX: document.

import os
import json
import shlex
import importlib
import subprocess

import dput.core
from dput.core import logger
from dput.exceptions import NoSuchConfigError, DputConfigurationError


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
    dput.core.mangle_sys()
    logger.trace("Loading object: %s" % (obj_path))
    module, obj = obj_path.rsplit(".", 1)
    mod = importlib.import_module(module)
    fltr = getattr(mod, obj)
    return fltr


def get_obj(klass, checker_method):
    # XXX: return (defn, obj), so we can use the stored .json file for more.
    logger.trace("Attempting to resolve %s %s" % (klass, checker_method))
    try:
        config = load_config(klass, checker_method)
    except NoSuchConfigError:
        logger.debug("failed to resolve config %s" % (checker_method))
        return None
    path = config['path']
    logger.trace("loading %s %s" % (klass, path))
    try:
        return load_obj(path)
    except ImportError:
        logger.warning("failed to resolve path %s" % (path))
        return None


def run_command(command):
    """
    Run a synchronized command. The argument must be a list of arguments.
    Returns a triple (stdout, stderr, exit_status)

    If there was a problem to start the supplied command, (None, None, -1) is
    returned
    """

    if not isinstance(command, list):
        command = shlex.split(command)
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


def get_configs(klass):
    configs = set()
    for path in dput.core.CONFIG_LOCATIONS:
        path = "%s/%s" % (path, klass)
        if os.path.exists(path):
            for fil in os.listdir(path):
                xtn = ".json"
                if fil.endswith(xtn):
                    configs.add(fil[:-len(xtn)])
    return configs


def _config_cleanup(obj):
    def do_add(new, old):
        if not isinstance(new, list) and not isinstance(old, list):
            raise Exception("WTF NOT LIST")  # XXX: better exception

        nset = set(new)
        oset = set(old)
        nobj = oset | nset
        return list(nobj)

    def do_sub(new, old):
        if not isinstance(new, list) and not isinstance(old, list):
            raise Exception("WTF NOT LIST")  # XXX: better exception
        nset = set(new)
        oset = set(old)
        nobj = oset - nset
        return list(nobj)

    def do_eql(new, old):
        return new

    operators = {
        "+": do_add,
        "-": do_sub,
        "=": do_eql
    }

    ret = obj.copy()
    trm = []
    for key in obj:
        operator = key[0]
        if operator not in operators:
            continue

        kname = key[1:]
        op = operators[operator]

        if kname in ret:
            ret[kname] = op(ret[key], ret[kname])
        else:
            ret[kname] = ret[key]
        ret.pop(key)
    return ret


def load_config(config_class, config_name, default=None):
    logger.debug("Loading configuration: %s %s" % (config_class,
                                            config_name))
    ret = {}
    template_path = "%s/%s/%s.json"
    for config in dput.core.CONFIG_LOCATIONS:
        logger.trace("Checking for configuration: %s" % (config))
        path = template_path % (
            config,
            config_class,
            config_name
        )
        logger.trace("Checking - %s" % (path))
        if os.path.exists(path):
            ret.update(json.load(open(path, 'r')))

    if 'meta' in ret and ret['meta'] != config_name:
        metainfo = load_config("metas", ret['meta'], default={})
        metainfo.update(ret)
        ret = metainfo

    return _config_cleanup(ret)

    if default is not None:
        return default

    logger.warning("Failed to load configuration")

    nsce = NoSuchConfigError("No such configuration: '%s' in class '%s'" % (
        config_name,
        config_class
    ))

    nsce.config_class = config_class
    nsce.config_name = config_name
    nsce.checked = dput.core.CONFIG_LOCATIONS
    raise nsce


def obj_docs(klass, ostr):
    """
    Get an object's docstring by name / class.
    """
    obj = get_obj(klass, ostr)
    if obj is None:
        raise DputConfigurationError("No such object: `%s'" % (
            ostr
        ))
    return obj.__doc__


def run_func_by_name(klass, name, changes, profile):
    logger.debug("running check: %s" % (name))
    obj = get_obj(klass, name)
    if obj is None:
        raise DputConfigurationError("No such obj: `%s'" % (
            name
        ))

    interface = 'cli'
    if 'interface' in profile:
        interface = profile['interface']
    logger.trace("Using interface %s" % (interface))
    interface_obj = get_obj('interfaces', interface)
    if interface_obj is None:
        raise DputConfigurationError("No such interface: `%s'" % (
            interface
        ))
    interface = interface_obj()
    interface.initialize()

    ret = obj(
        changes,
        profile,
        interface
    )

    interface.shutdown()
    return ret
