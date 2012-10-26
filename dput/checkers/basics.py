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
Basic and core package checkers.
"""

import re

from dput.core import logger
from dput.exceptions import ChangesFileException, CheckerException


class GPGCheckerError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``gpg`` checker encounters an issue.
    """
    pass


class HashValidationError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``checksum`` checker encounters an issue.
    """
    pass


class SuiteMismatchError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``suite-mismatch`` checker encounters an issue.
    """
    pass


class SourceMissingError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``source`` checker encounters an issue.
    """
    pass


class BadDistributionError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``allowed-distribution`` checker encounters an issue.
    """
    pass


class BinaryUploadError(CheckerException):
    """
    Subclass of the :class:`dput.exceptions.CheckerException`.

    Thrown if the ``check-debs`` checker encounters an issue.
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
        if profile['allow_unsigned_uploads'] and \
           profile['allow_unsigned_uploads'] != '0':
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
                           " checks." % (
                                model
                           ))
            return
    else:
        logger.warning("No `enforce` key in check-debs. Skipping checks.")
        return

    has_debs = False
    for fil in changes.get_files():
        xtn = '.deb'
        if fil.endswith(xtn):
            has_debs = True

    if enforce_debs and not has_debs:
        raise BinaryUploadError(
            "There are no .debs in this upload, and we're enforcing them."
        )
    if not enforce_debs and has_debs:
        raise BinaryUploadError(
            "There are .debs in this upload, and enforcing they don't exist."
        )


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


def check_distribution_matches(changes, profile, interface):
    """
    The ``suite-mismatch`` checker is a stock dput checker that checks packages
    intended for upload for matching Distribution and last Changelog target.

    Profile key: none

    This checker simply verified that the Changes' Distribution key matches
    the last changelog target. If the mixup is between experimental and
    unstable, it'll remind you to pass ``-c unstable -d experimental``
    to sbuild.
    """
    changelog_distribution = changes.get("Changes").split()[2].strip(';')
    intent = changelog_distribution.strip()
    actual = changes.get("Distribution").strip()
    if intent != actual:
        logger.info("Upload is targeting %s but the changes will hit %s" % (
            intent, actual))
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


def check_allowed_distribution(changes, profile, interface):
    """
    The ``allowed-distribution`` checker is a stock dput checker that checks
    packages intended for upload for a valid upload distribution.

    Profile key: none

    Example profile::

        {
            ...
            "allowed_distributions": "(?!UNRELEASED)"
            ...
        }

    The allowed_distributions key is in Python ``re`` syntax.
    """
    suite = changes['Distribution']
    if 'allowed_distributions' in profile:
        srgx = profile['allowed_distributions']
        if re.match(srgx, suite) is None:
            logger.debug("Distribution does not %s match '%s'" % (suite,
                                    profile['allowed_distributions']))
            raise BadDistributionError("'%s' doesn't match '%s'" % (
                suite,
                srgx
            ))

    if'distributions' in profile:
        allowed_dists = profile['distributions']
        if suite not in allowed_dists.split(","):
            raise BadDistributionError("'%s' doesn't contain distribution '%s'"
                                       % (suite, profile['distributions']))


def check_source_needed(changes, profile, interface):
    """
    The ``source`` checker is a stock dput checker that checks packages
    intended for upload for source attached.

    Profile key: none

    .. warning::
        This is all magic and pre-beta. Please don't rely on it.

    This simply checks, based on Debian policy rules, if the upload aught to
    have source attached.
    """

    debian_revision = changes.get("Version")
    if debian_revision.find("-") == -1:
        logger.trace("Package appears to be native")
        return
    logger.trace("Package appears to be non-native")

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
