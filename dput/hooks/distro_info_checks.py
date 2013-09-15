# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2013 dput authors
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

try:
    from distro_info import (DebianDistroInfo, UbuntuDistroInfo,
                             DistroDataOutdated)
except ImportError:
    logger.warning('Uploading to Ubuntu requires python-distro-info to be '
                   'installed')
    raise


class UnknownDistribution(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``supported-distribution`` checker encounters an issue.
    """
    pass


class UnsupportedDistribution(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``supported-distribution`` checker finds a release that isn't
    supported.
    """
    pass


def check_supported_distribution(changes, profile, interface):
    """
    The ``supported-distribution`` checker is a stock dput checker that checks
    packages intended for upload for a valid upload distribution.

    Profile key: supported-distribution
    """
    suite = changes['Distribution']
    if profile.get('codenames'):
        if '-' in suite:
            release, pocket = suite.split('-', 1)
        else:
            release, pocket = suite, 'release'

        codenames = profile['codenames']
        if codenames == 'ubuntu':
            distro_info = UbuntuDistroInfo()
            pockets = profile['supported-distribution']
            logger.critical(pockets)
            if pocket not in pockets['known']:
                raise UnknownDistribution("Unkown pocket: %s" % pocket)
            if pocket not in pockets['allowed']:
                raise UnknownDistribution(
                    "Uploads aren't permitted to pocket: %s" % pocket)
        elif codenames == 'debian':
            distro_info = DebianDistroInfo()
        else:
            raise UnknownDistribution("distro-info doesn't know about %s"
                                      % codenames)

        try:
            codename = distro_info.codename(release, default=release)
            if codename not in distro_info.all:
                raise UnsupportedDistribution('Unknown release %s' % release)
            if codename not in distro_info.supported():
                raise UnsupportedDistribution('Unsupported release %s'
                                              % release)
        except DistroDataOutdated:
            logger.warn('distro-info is outdated, '
                        'unable to check supported releases')
