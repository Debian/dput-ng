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
from dput.dsc import parse_dsc_file
from dput.exceptions import HookException

class SourceMissingError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``source`` checker encounters an issue.
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

        # TODO: It may be also well possible to find out if the new upload has
        #      a higher number than the previous. But that either needs a
        #      Python version parser, or a call to dpkg --compare-versions

    else:
        logger.debug(
            "Upload appears to be native, or packaging a new upstream version."
        )

    raise Exception("Intentional Barrier")
