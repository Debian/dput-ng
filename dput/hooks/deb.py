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
from dput.exceptions import HookException


class BinaryUploadError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``check-debs`` checker encounters an issue.
    """
    pass



def check_debs_in_upload(changes, profile, interface):
    """
    The ``check-debs`` checker is a stock dput checker that checks packages
    intended for upload for .deb packages.

    Profile key: ``foo``

    Example profile::

        {
            "skip": false,
            "enforce": "debs"
        }

    ``skip``    controls if the checker should drop out without checking
                for anything at all.

    ``enforce`` This controls what we check for. Valid values are
                "debs" or "source". Nonsense values will cause
                an abort.
    """
    debs = {}
    if 'check-debs' in profile:
        debs = profile['check-debs']

    section = changes.get_section()
    BYHAND = (section == "byhand")

    logger.debug("Is BYHAND: %s" % (BYHAND))
    logger.debug("   section value: %s" % (section))

    if 'skip' in debs and debs['skip']:
        logger.debug("Skipping deb checker.")
        return

    enforce_debs = True
    if 'enforce' in debs:
        model = debs['enforce']
        if model == 'debs':
            enforce_debs = True
        elif model == 'source':
            enforce_debs = False
        else:
            logger.warning("Garbage value for check-debs/enforce - is %s,"
                           " valid values are `debs` and `source`. Skipping"
                           " checks." % (model))
            return
    else:
        logger.warning("No `enforce` key in check-debs. Skipping checks.")
        return

    has_debs = False
    for fil in changes.get_files():
        xtns = ['.deb', '.udeb']
        for xtn in xtns:
            if fil.endswith(xtn):
                has_debs = True

    if enforce_debs and not has_debs and not BYHAND:
        raise BinaryUploadError(
            "There are no .debs in this upload, and we're enforcing them."
        )
    if not enforce_debs and has_debs:
        raise BinaryUploadError(
            "There are .debs in this upload, and enforcing they don't exist."
        )
