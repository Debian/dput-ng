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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

# XXX: document.

import os

from dput.core import logger


def make_delayed_upload(conf, delayed_days):
    """
    DELAYED uploads to ftp-master eventually means to use another incoming
    directory instead of the default. This is easy enough to be implemented

    Mangles the supplied configuration object
    """
    incoming_directory = os.path.join(
        conf['incoming'],
        "DELAYED",
        "%d-day" % (delayed_days)
    )
    logger.debug("overriding upload directory to %s" % (incoming_directory))
    conf['incoming'] = incoming_directory


def force_passive_ftp_upload(conf):
    """
    Force FTP to use passive mode.

    Mangles the supplied configuration object
    """
    logger.debug("overriding configuration to force FTP passive mode")
    conf['passive_ftp'] = True
