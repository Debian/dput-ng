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
import abc
from contextlib import contextmanager

import dput.conf
from dput.core import logger
from dput.checker import run_checker
from dput.util import (load_obj, load_config)
from dput.exceptions import NoSuchConfigError, DputConfigurationError


class AbstractUploader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config, profile):
        self._config = config
        self._profile = profile

    def _pre_hook(self):
        self._run_hook("pre_upload_command")

    def _post_hook(self):
        self._run_hook("post_upload_command")

    def _run_hook(self, hook):
        if hook in self._config and self._config[hook] != "":
            self.run_command(self._config[hook])

    @abc.abstractmethod
    def initialize(self, **kwargs):
        pass

    @abc.abstractmethod
    def upload_file(self, filename):
        pass

    @abc.abstractmethod
    def run_command(self, command):
        pass

    @abc.abstractmethod
    def shutdown(self):
        pass


def get_uploader(uploader_method):
    # XXX: return (defn, obj), so we can use the stored .json file for more.
    # XXX: refactor this and dput.checker.get_checker
    logger.debug("Attempting to resolve %s" % (uploader_method))
    try:
        config = load_config('uploaders', uploader_method)
    except NoSuchConfigError:
        logger.debug("failed to resolve %s" % (uploader_method))
        return None
    path = config['plugin']
    logger.debug("loading %s" % (path))
    try:
        return load_obj(path)
    except ImportError:
        logger.debug("failed to resolve %s" % (path))
        return None


@contextmanager
def uploader(uploader_method, config, profile):
    """
    Rent-a-uploader :)
    """
    klass = get_uploader(uploader_method)

    if not klass:
        logger.error("Failed to resolve method %s to an uploader class" %
                    (uploader_method))
        raise DputConfigurationError(
                        "Failed to resolve method %s to an uploader class" %
                    (uploader_method))

    obj = klass(config, profile)
    obj.initialize()
    obj._pre_hook()
    try:
        yield obj
    finally:
        obj._post_hook()
        obj.shutdown()


def invoke_dput(changes, host):
    conf = dput.conf.load_dput_configs(host)
    profile = dput.util.load_config(
        'profiles',
        host,
        default={}
    )

    if 'checkers' in profile:
        for checker in profile['checkers']:
            logger.debug("Running checker %s" % (checker))
            ch = run_checker(checker, changes, conf, profile)
    else:
        logger.debug("No checkers defined in the profile....")

    with uploader(conf['method'], conf, profile) as obj:
        for path in changes.get_files():
            logger.debug("Uploading %s => %s" % (
                os.path.basename(path),
                host
            ))
            obj.upload_file(path)
