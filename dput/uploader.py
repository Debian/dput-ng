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

import abc

from dput.util import (load_config, load_obj)
from dput.core import logger
from dput.exceptions import NoSuchConfigError


class AbstractUploader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def initialize(self, **kwargs):
        pass

    @abc.abstractmethod
    def upload_file(self, filename):
        pass

    @abc.abstractmethod
    def shutdown(self):
        pass


def get_uploader(uploader_method):
    logger.debug("Attempting to resolve %s" % (uploader_method))
    try:
        config = load_config('uploaders', uploader_method)
    except NoSuchConfigError as e:
        logger.debug("failed to resolve %s" % (uploader_method))
        return None
    path = config['plugin']
    logger.debug("loading %s" % (path))
    try:
        return load_obj(path)
    except ImportError:
        logger.debug("failed to resolve %s" % (path))
        return None
