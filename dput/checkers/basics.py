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

from dput.core import logger
from dput.exceptions import ChangesFileException, CheckerException

class GPGCheckerError(CheckerException):
    pass


class HashValidationError(CheckerException):
    pass


class SuiteMismatchError(CheckerException):
    pass


def check_gpg_signature(changes, dputcf, profile):
    if "allow_unsigned_uploads" in dputcf:
        if dputcf['allow_unsigned_uploads']:
            logger.info("Not checking GPG signature due to "
                        "allow_unsigned_uploads being set.")
            return

    try:
        changes.validate_signature()
    except ChangesFileException:
        raise GPGCheckerError(
            "No signature on %s" % (changes.get_filename())
        )


def validate_checksums(changes, dputcf, profile):
    try:
        changes.validate_checksums()
    except ChangesFileException:
        raise GPGCheckerError(
            "Bad checksums on %s" % (changes.get_filename())
        )


def check_distribution_matches_changelog(changes, dputcf, profile):
    changelog_distribution = changes.get("Changes").split()[2].strip(';')
    intent = changelog_distribution.strip()
    actual = changes.get("Distribution").strip()
    if intent != actual:
        logger.debug("Oh shit, %s != %s" % (intent, actual))
        err = "Upload is targeting `%s', but the changes will hit `%s'." % (
            intent,
            actual
        )
        if intent == 'experimental' and (
            actual == 'unstable' or
            actual == 'sid'
        ):
            err += \
              "\nLooks like you forgot -d experimental when invoking sbuild."
        raise SuiteMismatchError(err)
