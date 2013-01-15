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
"""
SCP Uploader implementation.

.. warning::
    This is deprecated. Please use SFTP
"""

import os.path

from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException
from dput.uploaders.sftp import find_username
from dput.util import run_command


class ScpUploadException(UploadException):
    """
    Thrown in the event of a problem connecting, uploading to or
    terminating the connection with the remote server. This is
    a subclass of :class:`dput.exceptions.UploadException`.
    """
    pass


class ScpUploader(AbstractUploader):
    """
    Provides an interface to upload files through SCP.

    This is a subclass of :class:`dput.uploader.AbstractUploader`
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        login = find_username(self._config)
        self._scp_base = ["scp", "-p", "-C"]
        # XXX: Timeout?
        if 'port' in self._config:
            self._scp_base += ("-P", "%s" % self._config['port'])
        self._scp_host = "%s@%s" % (login, self._config['fqdn'])
        logger.debug("Using scp to upload to %s" % (self._scp_host))
        logger.warning("SCP is deprecated. Please consider upgrading to SFTP.")

    def upload_file(self, filename, upload_filename=None):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """

        if not upload_filename:
            upload_filename = os.path.basename(filename)

        incoming = self._config['incoming']
        targetfile = "%s:%s" % (self._scp_host, os.path.join(incoming,
                                                             upload_filename))
        scp = self._scp_base + [filename, targetfile]
        #logger.debug("run: %s" % (scp))
        (_, e, x) = run_command(scp)
        if x != 0:
            raise ScpUploadException("Failed to upload %s to %s: %s" % (
                upload_filename, targetfile, e)
            )

    def shutdown(self):
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        pass
