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
FTP Uploader implementation.
"""

import ftplib
import os.path

from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException


class FtpUploadException(UploadException):
    """
    Thrown in the event of a problem connecting, uploading to or
    terminating the connection with the remote server. This is
    a subclass of :class:`dput.exceptions.UploadException`.
    """
    pass


class FtpUploader(AbstractUploader):
    """
    Provides an interface to upload files through FTP. Supports anonymous
    uploads only for the time being.

    This is a subclass of :class:`dput.uploader.AbstractUploader`
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        logger.debug("Logging into %s as %s" % (
            self._config["fqdn"],
            self._config["login"]
        ))

        conf = self._config['ftp'] if 'ftp' in self._config else {}
        timeout = conf['timeout'] if 'timeout' in conf else 10

        try:
            self._ftp = ftplib.FTP(
                self._config["fqdn"],
                self._config["login"],
                None,
                timeout=timeout
            )
        except Exception as e:
            raise FtpUploadException(
                "Could not establish FTP connection to %s: %s" % (
                    self._config['fqdn'],
                    e
                )
            )

        if self._config["passive_ftp"] or kwargs['passive_mode']:
            logger.debug("Enable PASV mode")
            self._ftp.set_pasv(True)
        if self._config["incoming"]:
            logger.debug("Change directory to %s" % (
                self._config["incoming"]
            ))
            try:
                self._ftp.cwd(self._config["incoming"])
            except ftplib.error_perm as e:
                raise FtpUploadException(
                    "Could not change directory to %s: %s" % (
                        self._config["incoming"],
                        e
                    )
                )

    def upload_file(self, filename, upload_filename=None):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """

        if not upload_filename:
            upload_filename = os.path.basename(filename)

        try:
            basename = "STOR %s" % (upload_filename)
            self._ftp.storbinary(basename, open(filename, 'rb'))
        except ftplib.error_perm as e:
            self.upload_write_error(e)
        except Exception as e:
            raise FtpUploadException("Could not upload file %s: %s" % (
                upload_filename,
                e
            ))

    def shutdown(self):
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        self._ftp.quit()
