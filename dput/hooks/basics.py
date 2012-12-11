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
Basic and core package hooks.
"""

import re


from dput.core import logger
from dput.exceptions import (ChangesFileException, HookException)
from dput.dsc import parse_dsc_file
from dput.interface import BUTTON_NO


class GPGCheckerError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``gpg`` checker encounters an issue.
    """
    pass


class HashValidationError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``checksum`` checker encounters an issue.
    """
    pass


class SuiteMismatchError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``suite-mismatch`` checker encounters an issue.
    """
    pass


class SourceMissingError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``source`` checker encounters an issue.
    """
    pass


class BadDistributionError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``allowed-distribution`` checker encounters an issue.
    """
    pass


class BinaryUploadError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``check-debs`` checker encounters an issue.
    """
    pass


def _find_previous_upload(package_name, package_distribution):
    # well, this code is broken.
    # hopefully that's obvious. Thing is, the missing bit to retrieve
    # this information is not implemented remote
    # Returns the previous version and a hash of orig.tar.gz tarballs of the
    # previous upload. Eventually.
    # XXX: What in the fuck?  :)

    import random
    return (
        "1.4.31-2", {
        "lighttpd_1.4.31.orig.tar.gz": random.choice([
            "7907b7167d639b8a8daab97e223249d5",
            "1337"])
        }
    )


def _parse_version(raw_version):
    (epoch, version, debian_version) = (0, None, 0)
    if not raw_version:
        return (epoch, version, debian_version)
    epoch_index = raw_version.find(":")
    if epoch_index >= 0:
        epoch = raw_version[0:epoch_index]
        raw_version = raw_version[epoch_index + 1:]
    debian_version_index = raw_version.rfind("-")
    if debian_version_index >= 0:
        debian_version = raw_version[debian_version_index + 1:]
        raw_version = raw_version[:debian_version_index]
    version = raw_version
    return (epoch, version, debian_version)


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
            "allowed_distributions": "(?!UNRELEASED)",
            "distributions": ["unstable", "testing"]
            ...
        }

    The allowed_distributions key is in Python ``re`` syntax.
    """
    suite = changes['Distribution']
    if 'allowed_distributions' in profile:
        srgx = profile['allowed_distributions']
        if re.match(srgx, suite) is None:
            logger.debug("Distribution does not %s match '%s'" % (
                suite,
                profile['allowed_distributions']
            ))
            raise BadDistributionError("'%s' doesn't match '%s'" % (
                suite,
                srgx
            ))

    if'distributions' in profile:
        allowed_dists = profile['distributions']
        if suite not in allowed_dists.split(","):
            raise BadDistributionError(
                "'%s' doesn't contain distribution '%s'" % (
                    suite,
                    profile['distributions']
                ))


def check_protected_distributions(changes, profile, interface):
    """
    The ``protected distributions`` checker is a stock dput checker that makes
    sure, users intending an upload for a special care archive (
    testing-proposed-updates, stable-security, etc.) did really follow the
    archive policies for that.

    Profile key: none

    """
    # XXX: This check does not contain code names yet. We need a global way
    #      to retrieve and share current code names.
    suite = changes['Distribution']
    query_user = False
    release_team_suites = ["testing-proposed-updates", "proposed-updates",
                           "stable", "testing"]
    if suite in release_team_suites:
        msg = "Are you sure to upload to %s? Did you coordinate with the " \
            "Release Team before your upload?" % (suite)
        error_msg = "Aborting upload to Release Team managed suite upon " \
            "request"
        query_user = True
    security_team_suites = ["stable-security", "oldstable-security",
                            "testing-security"]
    if suite in security_team_suites:
        msg = "Are you sure to upload to %s? Did you coordinate with the " \
            "Security Team before your upload?" % (suite)
        error_msg = "Aborting upload to Security Team managed suite upon " \
            "request"
        query_user = True

    if query_user:
        logger.trace("Querying the user for input. The upload targets a "
                     "protected distribution")
        if not interface.boolean('Protected Checker', msg, default=BUTTON_NO):
            raise BadDistributionError(error_msg)
        else:
            logger.warning("Uploading with explicit confirmation by the user")
    else:
        logger.trace("Nothing to do for checker protected_distributions")


def check_archive_integrity(changes, profile, interface):
    """
    The ``source`` checker is a stock dput checker that checks packages
    intended for upload for source attached.

    Profile key: none

    .. warning::
        This is all magic and pre-beta. Please don't rely on it.

    This simply checks, based on Debian policy rules, if the upload aught to
    have source attached.
    """

    package_version = changes.get("Version")
    package_name = changes.get("Source")
    package_distribution = changes.get("Distribution")
    dsc = parse_dsc_file(filename=changes.get_dsc())
    orig_tarballs = {}
    # technically this will also contain .debian.tar.gz or .diff.gz stuff.
    # We don't care.
    for files in dsc["Files"]:
        orig_tarballs[files['name']] = files['md5sum']

    (previous_version, previous_checksums) = _find_previous_upload(
        package_name,
        package_distribution
    )

    if previous_version:
        (p_ev, p_uv, p_dv) = _parse_version(previous_version)
        (c_ev, c_uv, c_dv) = _parse_version(package_version)

        logger.trace("Parsing versions: (old/new) %s/%s; debian: %s/%s" % (
            p_uv,
            c_uv,
            p_dv,
            c_dv
        ))

        if p_ev == c_ev and p_uv == c_uv:
            logger.trace("Upload %s/%s appears to be a Debian revision only" %
                         (package_name, package_version))
            for checksum in previous_checksums:
                if checksum in orig_tarballs:
                    logger.debug("Checking %s: %s == %s" % (
                        checksum,
                        previous_checksums[checksum],
                        orig_tarballs[checksum]
                    ))
                    if previous_checksums[checksum] != orig_tarballs[checksum]:
                        raise SourceMissingError(
                            "MD5 checksum for a Debian version only "
                            "upload for package %s/%s does not match the "
                            "archive's checksum: %s != %s" % (
                                package_name,
                                package_version,
                                previous_checksums[checksum],
                                orig_tarballs[checksum]
                            )
                        )
                else:
                    logger.debug("Checking %s: new orig stuff? %s" % (
                        checksum,
                        checksum  # XXX: This is wrong?
                    ))
                    raise SourceMissingError(
                        "Package %s/%s introduces new upstream changes: %s" % (
                            package_name,
                            package_version,
                            checksum
                        )
                    )
        else:
            logger.debug("Not checking archive integrity. "
                         "Upload %s/%s is packaging a new upstream version" %
                         (package_name, package_version))

        #TODO: It may be also well possible to find out if the new upload has
        #      a higher number than the previous. But that either needs a
        #      Python version parser, or a call to dpkg --compare-versions

    else:
        logger.debug(
            "Upload appears to be native, or packaging a new upstream version."
        )

    raise Exception("Intentional Barrier")
