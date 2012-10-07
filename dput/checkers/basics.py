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

import re

from dput.core import logger
from dput.exceptions import ChangesFileException, CheckerException


class GPGCheckerError(CheckerException):
    pass


class HashValidationError(CheckerException):
    pass


class SuiteMismatchError(CheckerException):
    pass


class SourceMissingError(CheckerException):
    pass


def check_gpg_signature(changes, dputcf, profile):
    if "allow_unsigned_uploads" in dputcf:
        if dputcf['allow_unsigned_uploads']:
            logger.info("Not checking GPG signature due to "
                        "allow_unsigned_uploads being set.")
            return

    try:
        changes.validate_signature()
    except ChangesFileException as e:
        raise GPGCheckerError(
            "No valid signature on %s: %s" % (changes.get_filename(),
                                              e)
        )


def validate_checksums(changes, dputcf, profile):
    try:
        changes.validate_checksums(check_hash=dputcf["hash"])
    except ChangesFileException as e:
        raise GPGCheckerError(
            "Bad checksums on %s: %s" % (changes.get_filename(), e)
        )


def check_distribution_matches(changes, dputcf, profile):
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


def check_source_needed(changes, dputcf, profile):

    debian_revision = changes.get("Version")
    if debian_revision.find("-") == -1:
        logger.debug("Package appears to be native")
        return
    logger.debug("Package appears to be non-native")

    debian_revision = debian_revision[debian_revision.rfind("-") + 1:]
    debian_revision = int(debian_revision)
    # policy 5.6.12:
    # debian_revision --
    # It is optional; if it isn't present then the upstream_version may not
    # contain a hyphen. This format represents the case where a piece of
    # software was written specifically to be a Debian package, where the
    # Debian package source must always be identical to the pristine source
    # and therefore no revision indication is required.

    orig_tarball_found = False
    for filename in changes.get_files():
        if re.search("orig\.tar\.(gz|bz2|lzma|xz)$", filename):
            orig_tarball_found = True
            break

    if debian_revision == 1 and not orig_tarball_found:
        raise SourceMissingError("Upload appears to be a new upstream " +
                            "version but does not include original tarball")
    elif debian_revision > 1 and orig_tarball_found:
        logger.warning("Upload appears to be a Debian specific change, " +
                       "but does include original tarball")

    # TODO: Are we insane doing this? e.g. consider -B uploads?
