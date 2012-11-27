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
This code deals with the reading and processing of Debian .dsc files.
"""

import os
import os.path

from debian import deb822
from dput.exceptions import DscFileException


class Dsc(object):
    """
    Changes object to help process and store information regarding Debian
    .dsc files, used in the upload process.
    """

    def __init__(self, filename=None, string=None):
        """
        Object constructor. The object allows the user to specify **either**:

        #. a path to a *changes* file to parse
        #. a string with the *changes* file contents.

        ::

        a = Dsc(filename='/tmp/packagename_version.changes')
        b = Dsc(string='Source: packagename\\nMaintainer: ...')

        ``filename``
            Path to *changes* file to parse.

        ``string``
            *dsc* file in a string to parse.
        """
        if (filename and string) or (not filename and not string):
            raise TypeError

        if filename:
            self._absfile = os.path.abspath(filename)
            self._data = deb822.Dsc(file(filename))
        else:
            self._data = deb822.Dsc(string)

        if len(self._data) == 0:
            raise DscFileException('Changes file could not be parsed.')
        if filename:
            self.basename = os.path.basename(filename)
        else:
            self.basename = None
        self._directory = ""

    def __getitem__(self, key):
        """
        Returns the value of the rfc822 key specified.

        ``key``
            Key of data to request.
        """
        return self._data[key]

    def __contains__(self, key):
        """
        Returns whether the specified RFC822 key exists.

        ``key``
            Key of data to check for existence.
        """
        return key in self._data

    def get(self, key, default=None):
        """
        Returns the value of the rfc822 key specified, but defaults
        to a specific value if not found in the rfc822 file.

        ``key``
            Key of data to request.

        ``default``
            Default return value if ``key`` does not exist.
        """
        return self._data.get(key, default)


def parse_dsc_file(filename, directory=None):
    """
    Parse a .dsc file and return a dput.changes.Dsc instance with
    parsed changes file data. The optional directory argument refers to the
    base directory where the referred files from the changes file are expected
    to be located.

    XXX: The directory argument is ignored
    """
    _c = Dsc(filename=filename)
    return(_c)
