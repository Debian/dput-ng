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
"""
SFTP Uploader implementation
"""

import paramiko
import os.path

from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException


class SftpUploadException(UploadException):
    """
    Thrown in the event of a problem connecting, uploading to or
    terminating the connection with the remote server. This is
    a subclass of :class:`dput.exceptions.UploadException`.
    """
    pass


def find_username(conf):
    """
    Given a profile (``conf``), return the prefered username to login
    with. It falls back to getting the logged in user's name.
    """
    user = os.getlogin()  # XXX: This needs a controlling terminal
    if 'login' in conf:
        new_user = conf['login']
        if new_user != "*":
            user = new_user
    return user


class SFTPUploader(AbstractUploader):
    """
    Provides an interface to upload files through SFTP.

    This is a subclass of :class:`dput.uploader.AbstractUploader`
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        fqdn = self._config['fqdn']
        incoming = self._config['incoming']

        if incoming[0] == '~':
            raise SftpUploadException("SFTP doesn't support ~path or ~/path. "
                                      "if you need $HOME paths, use SCP.")

        ssh_kwargs = {
            "port": 22,  # XXX: Allow overrides
            "compress": True
        }

        config = paramiko.SSHConfig()
        config.parse(open(os.path.expanduser('~/.ssh/config')))
        o = config.lookup(fqdn)

        user = find_username(self._config)
        if "user" in o:
            user = o['user']

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

    def _auth(self, fqdn, ssh_kwargs, _first=0):
        if _first == 3:
            raise SftpUploadException("Failed to authenticate")
        try:
            self._sshclient.connect(fqdn, **ssh_kwargs)
            logger.info("Logged in!")
        except paramiko.AuthenticationException:
            logger.warning("Failed to auth. Prompting for a login pair.")
            user, pw = self.prompt_ui('please login', [
                {'msg': 'Username', 'show': True},  # XXX: Ask for pw only
                {'msg': 'Password', 'show': False}         # 4 first error
            ])
            if user is not None:
                ssh_kwargs['username'] = user
            ssh_kwargs['password'] = pw
            self._auth(fqdn, ssh_kwargs, _first=_first + 1)

    def upload_file(self, filename):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """
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
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        self._sshclient.close()
        self._sftp.close()
