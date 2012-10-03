# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2012 dput authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your Option) any later version.
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
from dput.exceptions import SftpUploadException
from dput.uploader import AbstractUploader
from dput.conf import Opt

import paramiko
import os.path

#paramiko.util.log_to_file('/tmp/paramiko.log')

class SFTPUpload(AbstractUploader):

    def initialize(self, **kwargs):
        self._transport = paramiko.Transport((self._config[Opt.KEY_FQDN],
                                              self._config[Opt.KEY_SFTP_PORT]))

        try:
            private_key = None
            if self._config[Opt.KEY_SFTP_PRIVATE_KEY]:
                if self._config[Opt.KEY_SFTP_PRIVATE_KEY].startswith("~"):
                    private_key_file = os.path.expanduser(
                                    self._config[Opt.KEY_SFTP_PRIVATE_KEY])
                else:
                    private_key_file = self._config[Opt.KEY_SFTP_PRIVATE_KEY]
                logger.debug("Authenticate using private key %s" %
                              (private_key_file))

                if not os.access(private_key_file, os.R_OK):
                    raise SftpUploadException("Key file %s is not accessible" %
                                               (private_key_file))
                private_key = paramiko.RSAKey.from_private_key_file(
                                                            private_key_file)

            user = self._config[Opt.KEY_SFTP_USERNAME]
            password = None

            logger.debug("SFTP user: %s; password: %s" %
                         (user, "YES" if password else "NO"))

            self._transport.connect(username=user, password=password,
                                    pkey=private_key)
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        except paramiko.AuthenticationException as e:
            raise SftpUploadException(
                                "Failed to authenticate with server %s: %s" %
                                (self._config[Opt.KEY_FQDN], e))


        try:
            self._sftp.chdir(self._config[Opt.KEY_INCOMING])
        except IOError as e:
            raise SftpUploadException("Could not change directory to %s: %s" %
                                       (self._config[Opt.KEY_INCOMING], e))

    def upload_file(self, filename):
        basename = os.path.basename(filename)
        try:
            self._sftp.put(basename, filename)
        except IOError as e:
            if e.errno == 13:
                logger.warning("Could not overwrite file. blah blah blah")
            else:
                raise SftpUploadException("Could not upload file %s: %s" %
                                          (filename, e))

    def shutdown(self):
        self._sftp.close()
        self._transport.close()

    def run_command(self, command):
        raise NotImplementedError("Not implemented for the SFTP uploader")
