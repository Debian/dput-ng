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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""
Local Uploader implementation
"""

from dput.uploader import AbstractUploader
import dput.util
import os.path


class LocalUploader(AbstractUploader):
    """
    Provides an interface to "upload" files to the local filesystem. This
    is helpful when you're dputting to the same system you're currently on,
    and do not wish to use `scp` or `sftp` as the transport (which is totally
    understandable).
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        pass

    def upload_file(self, filename, upload_filename=None):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """

        #TODO: Fix me later. install does not support renaming
        assert(upload_filename is None)

        whereto = self._config['incoming']
        whereto = os.path.expanduser(whereto)
        if "HOME" in os.environ:
            whereto = os.path.join(os.environ["HOME"], whereto)
        dput.util.run_command([
            "install",
            filename,
            whereto
        ])

    def shutdown(self):
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        pass
