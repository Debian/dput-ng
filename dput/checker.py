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
from dput.util import (load_config, load_obj)
from dput.changes import Changes
from dput.exceptions import NoSuchConfigError


def get_checker(checker_method):
    # XXX: return (defn, obj), so we can use the stored .json file for more.
    # XXX: refactor this and dput.uploader.get_uploader
    logger.debug("Attempting to resolve checker %s" % (checker_method))
    try:
        config = load_config('checkers', checker_method)
    except NoSuchConfigError:
        logger.debug("failed to resolve %s" % (checker_method))
        return None
    path = config['plugin']
    logger.debug("loading checker %s" % (path))
    try:
        return load_obj(path)
    except ImportError:
        logger.debug("failed to resolve %s" % (path))
        return None


def run_checker(checker, path, dput_config):
    logger.debug("running checker: %s" % (checker))
    obj = get_checker(checker)
    # XXX: throw error if obj == None
    ch = Changes(filename=path)
    profile = {}  # XXX: add in real profile stuff from host thinger
    return obj(
        ch,
        dput_config,
        profile
    )
