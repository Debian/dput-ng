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

import re

from dput.core import logger
from dput.util import load_config
from dput.exceptions import HookException
from dput.interface import BUTTON_NO


class BadDistributionError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``allowed-distribution`` checker encounters an issue.
    """
    pass


class SuiteMismatchError(HookException):
    """
    Subclass of the :class:`dput.exceptions.HookException`.

    Thrown if the ``suite-mismatch`` checker encounters an issue.
    """
    pass


def check_allowed_distribution(changes, profile, interface):
    """
    The ``allowed-distribution`` checker is a stock dput checker that checks
    packages intended for upload for a valid upload distribution.

    Profile key: none

    Example profile::

        {
            ...
            "allowed_distributions": "(?!UNRELEASED)",
            "distributions": ["unstable", "testing"],
            "disallowed_distributions": []
            ...
        }

    The allowed_distributions key is in Python ``re`` syntax.
    """
    allowed_block = profile.get('allowed-distribution', {})
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

    if 'disallowed_distributions' in profile:
        disallowed_dists = profile['disallowed_distributions']
        if suite in disallowed_dists:
            raise BadDistributionError("'%s' is in '%s'" % (
                suite, disallowed_dists))

    if 'codenames' in profile and profile['codenames']:
        codenames = load_config('codenames', profile['codenames'])
        blocks = allowed_block.get('codename-groups', [])
        if blocks != []:
            failed = True
            for block in blocks:
                names = codenames.get(block, [])
                if suite in names:
                    failed = False

            if failed:
                raise BadDistributionError("`%s' not in the codename group" % (
                    suite
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
