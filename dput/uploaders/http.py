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
HTTP Uploader implementation
"""

from dput.exceptions import UploadException
from dput.uploader import AbstractUploader
from dput.core import logger

import mmap
import urllib.parse
import urllib.request
import os.path
import mimetypes


class HttpUploadException(UploadException):
    """
    Thrown in the event of a problem connecting, uploading to or
    terminating the connection with the remote server. This is
    a subclass of :class:`dput.exceptions.UploadException`.
    """
    pass


class HTTPUploader(AbstractUploader):
    """
    Provides an interface to upload files through HTTP. Supports only anonymous
    uploads for the time being.

    This is a subclass of :class:`dput.uploader.AbstractUploader`
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        mimetypes.init()

        # code below is fugly. Dear god, please write a mutable
        # urlparse library. Pretty please. Hopefully the mangling below is
        # reasonably sane
        if not self._config['fqdn'].lower().startswith("http"):
            self._config['fqdn'] = "{}://{}".format(
                self._config['method'], self._config['fqdn'])
        self._baseurl = urllib.parse.urlparse(self._config['fqdn'])

        _netloc = self._baseurl.hostname
        if self._baseurl.port:
            _netloc += ":" + str(self._baseurl.port)

        _incoming = self._config['incoming']
        if not _incoming.startswith("/"):
            _incoming = "/" + _incoming
        if not _incoming.endswith("/"):
            _incoming = _incoming + "/"

        _path = self._baseurl.path
        if not _path:
            _path = _incoming
        else:
            _path = _path + _incoming

        _params = self._baseurl.params
        _query = self._baseurl.query
        _fragment = self._baseurl.fragment

        self._username = self._baseurl.username
        self._password = self._baseurl.password

        # XXX: Timeout, please.

        self._baseurl = urllib.parse.urlunparse((self._baseurl.scheme,
                                             _netloc, _path,
                                             _params, _query, _fragment))

    def upload_file(self, filename, upload_filename=None):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """
        upload_filename = self._baseurl + os.path.basename(filename)
        logger.debug("Upload to %s" % (upload_filename))

        (mime_type, _) = mimetypes.guess_type(filename)
        fh = open(filename, 'rb')
        mmaped_fh = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        req = urllib.request.Request(
            url=upload_filename,
            data=fh.read(),
            method='PUT',
        )
        if mime_type is not None:
            req.add_header("Content-Type", mime_type)

        if self._username is not None:
            try:
                password_mgr = urllib.request.HTTPPasswordMgrWithPriorAuth()
                password_mgr.add_password(None, self._baseurl, self._username, self._password, is_authenticated=True)
            except AttributeError:
                password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, self._baseurl, self._username, self._password)
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
        else:
            opener = urllib.request.build_opener()

        try:
            opener.open(req)
        except urllib.error.HTTPError as e:
            error_message = e.read().decode(
                e.headers.get_content_charset(failobj='utf-8'))
            if error_message:
                error_message = error_message.strip()
                if "\n" in error_message:
                    error_message = "\n\t" + "\n\t".join(error_message.splitlines())
                logger.warning("HTTP error message: %s" % error_message)
            if e.code == 403:
                self.upload_write_error(e)
            else:
                raise HttpUploadException(e)
        mmaped_fh.close()
        fh.close()

    def shutdown(self):
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        pass
