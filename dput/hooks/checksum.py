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
from dput.exceptions import (ChangesFileException, HookException)


class HashValidationError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``checksum`` checker encounters an issue.
    """
    pass


def validate_checksums(changes, profile, interface):
    """
    The ``checksum`` checker is a stock dput checker that checks packages
    intended for upload for correct checksums. This is actually the most
    simple checker that exists.

    Profile key: none.

    Example profile::

        {
            ...
            "hash": "md5"
            ...
        }

    The hash may be one of md5, sha1, sha256.
    """
    try:
        changes.validate_checksums(check_hash=profile["hash"])
    except ChangesFileException as e:
        raise HashValidationError(
            "Bad checksums on %s: %s" % (changes.get_filename(), e)
        )
