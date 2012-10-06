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

from dput.exceptions import UploadException
from dput.uploader import AbstractUploader
from dput.core import logger
from dput.conf import Opt

import urllib2
import mmap
import mimetypes
import os.path
import urlparse

class HttpUploadException(UploadException):
    pass

class HTTPUpload(AbstractUploader):
    def initialize(self, **kwargs):
        mimetypes.init()


        # code below is fugly. Dear god, please write a mutable
        # urlparse library. Pretty please. Hopefully the mangling below is
        # reasonably sane
        if not self._config[Opt.KEY_FQDN].lower().startswith("http"):
            self._config[Opt.KEY_FQDN] = "http://" + self._config[Opt.KEY_FQDN]
        self._baseurl = urlparse.urlparse(self._config[Opt.KEY_FQDN])


        _incoming = self._config[Opt.KEY_INCOMING]
        if not _incoming.startswith("/"):
            _incoming = "/" + _incoming
        if not _incoming.endswith("/"):
            _incoming = _incoming + "/"

        _path = self._baseurl.path
        if not _path:
            _path = _incoming
        else:
            _path = _path + _incoming

        _query = self._baseurl.query
        self._username = self._baseurl.username
        self._password = self._baseurl.password

        self._baseurl = urlparse.urlunparse((self._baseurl.scheme,
                                             self._baseurl.netloc, _path,
                                             _query, self._username,
                                             self._password
                                             ))


    def upload_file(self, filename):

        upload_filename = self._baseurl + os.path.basename(filename)
        logger.debug("Upload to %s" % (upload_filename))

        (mime_type, _) = mimetypes.guess_type(filename)
        fh = open(filename, 'rb')
        mmaped_fh = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
        req = urllib2.Request(url=upload_filename, data=mmaped_fh)
        req.add_header("Content-Type", mime_type)
        req.get_method = lambda: 'PUT'

        try:
            urllib2.urlopen(req)
        except urllib2.HTTPError as e:
            if e.code == 403:
                self.upload_write_error(e)
            else:
                raise HttpUploadException(e)
        mmaped_fh.close()
        fh.close()



    def shutdown(self):
        pass
