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


class GPGCheckerError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``gpg`` checker encounters an issue.
    """
    pass


def check_gpg_signature(changes, profile, interface):
    """
    The ``gpg`` checker is a stock dput checker that checks packages
    intended for upload for a GPG signature.

    Profile key: ``gpg``

    Example profile::

        {
            "allowed_keys": [
                "8F049AD82C92066C7352D28A7B585B30807C2A87",
                "B7982329"
            ]
        }

    ``allowed_keys`` is an optional entry which contains all the keys that
    may upload to this host. This can come in handy if you use more then one
    key to upload to more then one host. Use any length of the last N chars
    of the fingerprint.
    """

    if "allow_unsigned_uploads" in profile:
        if profile['allow_unsigned_uploads']:
            logger.info("Not checking GPG signature due to "
                        "allow_unsigned_uploads being set.")
            return

    gpg = {}
    if 'gpg' in profile:
        gpg = profile['gpg']

    try:
        key = changes.validate_signature()
        if 'allowed_keys' in gpg:
            allowed_keys = gpg['allowed_keys']

            found = False
            for k in allowed_keys:
                if k == key[-len(k):]:
                    logger.info("Key %s is trusted to upload to this host." % (
                        k
                    ))
                    found = True

            if not found:
                raise GPGCheckerError("Key %s is not in %s" % (
                    key,
                    allowed_keys
                ))

    except ChangesFileException as e:
        raise GPGCheckerError(
            "No valid signature on %s: %s" % (changes.get_filename(),
                                              e)
        )
