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
Misc & helper functions
"""

import os
import json
import shlex
import importlib
import subprocess
import validictory
from contextlib import contextmanager

import dput.core
from dput.core import logger
from dput.exceptions import (NoSuchConfigError, DputConfigurationError,
                             InvalidConfigError)


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
    dput.core.mangle_sys()
    logger.trace("Loading object: %s" % (obj_path))
    module, obj = obj_path.rsplit(".", 1)
    mod = importlib.import_module(module)
    fltr = getattr(mod, obj)
    return fltr


def get_obj(klass, checker_method):  # checker_method is a bad name.
    """
    Get an object by plugin def (``checker_method``) in class ``klass`` (such
    as ``processors`` or ``checkers``).
    """
    logger.trace("Attempting to resolve %s %s" % (klass, checker_method))
    try:
        config = load_config(klass, checker_method, schema='plugin')
        if config is None or config == {}:
            raise NoSuchConfigError("No such config")
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
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError as e:
        logger.error("Could not execute %s: %s" % (" ".join(command), e))
        return (None, None, -1)
    (output, stderr) = pipe.communicate()
    #if pipe.returncode != 0:
    #   error("Command %s returned failure: %s" % (" ".join(command), stderr))
    return (output, stderr, pipe.returncode)


def get_configs(klass):
    """
    Get all valid config targets for class ``klass``.
    """
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
    """
    Handle merging plus, minus and set fields. Internal only.
    """
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


def load_config(config_class, config_name,
                default=None, schema=None,
                configs=None):
    """
    Load any dput configuration given a ``config_class`` (such as
    ``checkers`` or ``profiles``), and a ``config_name`` (such as
    ``lintian`` or ``tweet``).

    Optional kwargs:

        ``default`` is a default to return, in case the config file
        isn't found. If this isn't provided, this function will
        raise a :class:`dput.exceptions.NoSuchConfigError`.

        ``schema`` is a schema to check the return value against,
        before returning it. This reads validictory syntax. If it's
        violated, this will raise a
        :class:`dput.exceptions.InvalidConfigError`.

        ``configs`` is a list of config files to check. When this
        isn't provided, we check dput.core.CONFIG_LOCATIONS.
    """

    logger.debug("Loading configuration: %s %s" % (
        config_class,
        config_name
    ))
    roots = []
    ret = {}
    found = False
    template_path = "%s/%s/%s.json"
    locations = configs or dput.core.CONFIG_LOCATIONS
    for config in locations:
        logger.trace("Checking for configuration: %s" % (config))
        path = template_path % (
            config,
            config_class,
            config_name
        )
        logger.trace("Checking - %s" % (path))
        try:
            if os.path.exists(path):
                found = True
                roots.append(path)
                ret.update(json.load(open(path, 'r')))
        except ValueError as e:
            raise DputConfigurationError("syntax error in %s: %s" % (
                path, e
            ))

    if not found:
        if default is not None:
            return default

        raise NoSuchConfigError("No such config: %s/%s" % (
            config_class,
            config_name
        ))

    if 'meta' in ret and ret['meta'] != config_name:
        metainfo = load_config("metas", ret['meta'],
                               default={}, configs=configs)
        for key in metainfo:
            if not key in ret:
                ret[key] = metainfo[key]
            else:
                logger.trace("Ignoring key %s for %s (%s)" % (
                    key,
                    ret['meta'],
                    metainfo[key]
                ))

    obj = _config_cleanup(ret)
    if schema is not None:
        sobj = None
        for root in dput.core.SCHEMA_DIRS:
            if sobj is not None:
                logger.debug("Skipping %s" % (root))
                continue

            logger.debug("Loading schema %s from %s" % (schema, root))
            spath = "%s/%s.json" % (
                root,
                schema
            )
            try:
                if os.path.exists(spath):
                    sobj = json.load(open(spath, 'r'))
                else:
                    logger.debug("No such config: %s" % (spath))
            except ValueError as e:
                raise DputConfigurationError("syntax error in %s: %s" % (
                    spath,
                    e
                ))

        if sobj is None:
            logger.critical("Schema not found: %s" % (schema))
            raise DputConfigurationError("No such schema: %s" % (schema))

        try:
            validictory.validate(obj, sobj)
        except validictory.validator.ValidationError as e:
            err = str(e)
            error = "Error with config file %s/%s - %s" % (
                config_class,
                config_name,
                err
            )
            ex = InvalidConfigError(error)
            ex.obj = obj
            ex.root = e
            ex.config_class = config_class
            ex.config_name = config_name
            ex.sdir = dput.core.SCHEMA_DIRS
            ex.schema = schema
            ex.roots = roots
            raise ex

    if obj != {}:
        return obj

    if default is not None:
        return default

    logger.debug("Failed to load configuration %s" % (config_name))

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
    Get an object's docstring by name / class def.
    """
    obj = get_obj(klass, ostr)
    if obj is None:
        raise DputConfigurationError("No such object: `%s'" % (
            ostr
        ))
    return obj.__doc__


@contextmanager
def get_obj_by_name(klass, name, profile):
    """
    Run a function, defined by ``name``, filed in class ``klass``
    """
    logger.trace("running %s: %s" % (klass, name))
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

    try:
        yield (obj, interface)
    finally:
        pass

    interface.shutdown()


def run_func_by_name(klass, name, changes, profile):
    """
    Run a function, defined by ``name``, filed in class ``klass``,
    with a :class:`dput.changes.Changes` (``changes``), and profile
    ``profile``.

    This is used to run the checkers / processors, internally.
    """
    with get_obj_by_name(klass, name, profile) as(obj, interface):
        obj(changes, profile, interface)
