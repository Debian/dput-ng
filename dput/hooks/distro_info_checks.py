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
    logger.warning('Uploading to Ubuntu requires python3-distro-info to be '
                   'installed')
    raise


class UnknownDistribution(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the checker encounters an issue.
    """
    pass


class UnsupportedDistribution(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``supported-distribution`` checker finds a release that isn't
    supported.
    """
    pass


class FieldEmptyException(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``required_fields`` checker finds an empty field that should
    be non-empty.
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


def required_fields(changes, profile, interface):
    """
    The ``required-fields`` checker is a stock dput checker that checks if the
    specified fields are non-empty in the Changes file, if the upload is
    targetting a specified distribution.

    Profile key: ```required-fields```

    Example profile::

        "required-fields": {
            ...
            "suites": "any-stable",
            "fields": ["Launchpad-Bugs-Fixed"],
            "skip": false
            ...
        }


    ``skip``    controls if the checker should drop out without checking
                for anything at all.

    ``fields``   This controls what we check for. Any fields present in this
                 list must be present and non-empty in the ```.changes``` file
                 being uploaded.

    ```suites``` This controls which target suites the check is active for. It
                 is a list containing suite names, or the special keywords
                 "any-stable" or "devel". If the field is missing or empty,
                 this check is active for all targets.
    """
    required_fields = profile.get('required-fields')
    if required_fields is None:
        return

    if required_fields.get('skip', True):
        return

    applicable_distributions = set(required_fields.get('suites', []))

    codenames = profile['codenames']
    if codenames == 'ubuntu':
        distro_info = UbuntuDistroInfo()
    elif codenames == 'debian':
        distro_info = DebianDistroInfo()
    else:
        raise UnknownDistribution("distro-info doesn't know about %s"
                                  % codenames)

    if 'any-stable' in applicable_distributions:
        applicable_distributions.remove('any-stable')

        supported = set(distro_info.supported())
        if 'devel' not in applicable_distributions:
            supported -= set([distro_info.devel(), 'experimental'])

        applicable_distributions |= supported

    if 'devel' in applicable_distributions and \
            'any-stable' not in applicable_distributions:
                # if any-stable is in there, it'll have done this already
                applicable_distributions.remove('devel')
                applicable_distributions.add(distro_info.devel())

    for codename in applicable_distributions:
        if codename not in distro_info.all:
            raise UnsupportedDistribution('Unknown release %s' % codename)

    distribution = changes.get("Distribution").strip()

    logger.debug("required-fields: Applying hook for %s" %
                 applicable_distributions)

    if distribution not in applicable_distributions:
        return

    for field in required_fields["fields"]:
        try:
            value = changes[field]
            if not value:
                raise FieldEmptyException(
                        "The field '%s' is required for upload to '%s', "
                        "but it is empty." % (field, distribution))
        except KeyError:
            raise FieldEmptyException(
                    "The field '%s' is required for uplaods to '%s', "
                    "but it is missing." % (field, distribution))
