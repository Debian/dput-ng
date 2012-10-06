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

import paramiko

import os.path

from dput.conf import Opt
from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException


class SftpUploadException(UploadException):
    pass


class SFTPUpload(AbstractUploader):
    def initialize(self, **kwargs):
        fqdn = self._config[Opt.KEY_FQDN]  # XXX: This is ugly.

        config = paramiko.SSHConfig()
        config.parse(open(os.path.expanduser('~/.ssh/config')))
        o = config.lookup(fqdn)

        ssh_kwargs = {
            "username": o['user'],
            "key_filename": os.path.expanduser(o['identityfile'])
        }

        self._sshclient = paramiko.SSHClient()
        self._sshclient.load_system_host_keys()
        self._sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._sshclient.connect(fqdn, **ssh_kwargs)
        self._sftp = self._sshclient.open_sftp()

    def upload_file(self, filename):
        basename = os.path.basename(filename)
        try:
            self._sftp.put(filename, basename)
        except IOError as e:
            if e.errno == 13:
                logger.warning("Could not overwrite file. blah blah blah")
            else:
                raise SftpUploadException("Could not upload file %s: %s" %
                                          (filename, e))

    def shutdown(self):
        self._sshclient.close()
        self._sftp.close()

    def run_command(self, command):
        raise NotImplementedError("Not implemented for the SFTP uploader")
