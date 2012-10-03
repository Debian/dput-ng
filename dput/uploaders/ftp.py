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

from dput.core import logger
from dput.exceptions import FtpUploadException
from dput.uploader import AbstractUploader
from dput.conf import Opt

import ftplib
import os.path


class FtpUploader(AbstractUploader):
    """
    Provides an interface to upload files through FTP. Supports anonymous
    uploads only for the time being
    """

    def initialize(self, **kwargs):
        try:
            self._ftp = ftplib.FTP(self._config[Opt.KEY_FQDN],
                                self._config[Opt.KEY_LOGIN], None, timeout=10)
        except Exception as e:
            raise FtpUploadException(
                            "Could not establish FTP connection to %s: %s" %
                            (self._config[Opt.KEY_FQDN], e))

        if self._config[Opt.KEY_PASSIVE_FTP] or kwargs['passive_mode']:
            logger.debug("Enable PASV mode")
            self._ftp.set_pasv(True)
        if self._config[Opt.KEY_INCOMING]:
            logger.debug("Change directory to %s"
                         % (self._config[Opt.KEY_INCOMING]))
            try:
                self._ftp.cwd(self._config[Opt.KEY_INCOMING])
            except ftplib.error_perm as e:
                raise FtpUploadException(
                                   "Could not change directory to %s: %s" %
                                   (self._config[Opt.KEY_INCOMING], e))

    def upload_file(self, filename):
        try:
            basename = "STOR %s" % (os.path.basename(filename))
            self._ftp.storbinary(basename, open(filename, 'rb'))
        except ftplib.error_perm as e:
            #TODO: Steal dput's warning here.
            logger.warning("Could not overwrite file. blah blah blah")
        except Exception as e:
            raise FtpUploadException("Could not upload file %s: %s" %
                                     (filename, e))

    def run_command(self, command):
        raise NotImplementedError("Not implemented for the FTP uploader")

    def shutdown(self):
        self._ftp.quit()
