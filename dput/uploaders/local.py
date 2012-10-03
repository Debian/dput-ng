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

from dput.uploader import AbstractUploader
import dput.util
import os


class LocalUploader(AbstractUploader):
    """
    Provides an interface to "upload" files to the local filesystem. This
    is helpful when you're dputing to the same system you're currently on,
    and do not wish to use `scp` or `sftp` as the transport (which is totally
    understandable).
    """

    def initialize(self):
        pass

    def upload_file(self, filename):
        # To upload a file, all we really need is to know, well,
        # where to upload it.
        whereto = self._config['incoming']
        dput.util.cp(filename, whereto)

    def run_command(self, command):
        dput.util.run_command(command)


    def shutdown(self):
        pass
