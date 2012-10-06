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

import getpass
import paramiko

import sys
import os.path

from dput.conf import Opt
from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException


class SftpUploadException(UploadException):
    pass


def query_for_creds():
    sys.stdout.write("Username: ")
    user = sys.stdin.readline().strip()
    pw = getpass.getpass()
    return (user, pw)


# XXX: Document this more :)
class SFTPUpload(AbstractUploader):
    def initialize(self, **kwargs):
        fqdn = self._config[Opt.KEY_FQDN]  # XXX: This is ugly.
        incoming = self._config[Opt.KEY_INCOMING]
        user = os.getlogin()  # XXX: This needs a controlling terminal

        ssh_kwargs = {}

        config = paramiko.SSHConfig()
        config.parse(open(os.path.expanduser('~/.ssh/config')))
        o = config.lookup(fqdn)

        if "user" in o:
            user = o['user']

        if 'login' in self._config:
            new_user = self._config[Opt.KEY_LOGIN]
            if new_user != "*":
                user = new_user

        ssh_kwargs['username'] = user

        if 'identityfile' in o:
            pkey = os.path.expanduser(o['identityfile'])
            ssh_kwargs['key_filename'] = pkey

        logger.info("Logging into host %s as %s" % (fqdn, user))
        self._sshclient = paramiko.SSHClient()
        self._sshclient.load_system_host_keys()
        self._sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._auth(fqdn, ssh_kwargs)
        self._sftp = self._sshclient.open_sftp()
        logger.debug("Changing directory to %s" % (incoming))
        self._sftp.chdir(incoming)

    def _auth(self, fqdn, ssh_kwargs):
        try:
            self._sshclient.connect(fqdn, **ssh_kwargs)
            logger.info("Logged in!")
        except paramiko.AuthenticationException:
            logger.warning("Failed to auth. Prompting for a login pair.")
            user, pw = query_for_creds()
            ssh_kwargs['username'] = user
            ssh_kwargs['password'] = pw
            self._auth(fqdn, ssh_kwargs)

    def upload_file(self, filename):
        basename = os.path.basename(filename)
        try:
            self._sftp.put(filename, basename)
        except IOError as e:
            if e.errno == 13:
                self.upload_write_error(e)
            else:
                raise SftpUploadException("Could not upload file %s: %s" %
                                          (filename, e))

    def shutdown(self):
        self._sshclient.close()
        self._sftp.close()
