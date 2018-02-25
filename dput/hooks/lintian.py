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
Lintian checker implementation
"""

from __future__ import print_function

import subprocess

from dput.core import logger
from dput.exceptions import HookException, DputConfigurationError
from dput.interface import BUTTON_NO


class LintianHookException(HookException):
    pass


def process(output):
    ret = []
    for line in output.splitlines():
        flag, line = line.split(":", 1)
        flag = flag.strip()
        if flag == "N":
            continue
        line = line.strip()
        component, line = line.split(":", 1)
        component = component.strip()
        line = line.strip()
        payload = line.split(" ", 1)

        if len(payload) > 1:
            tag, info = payload
        else:
            tag = payload[0]
            info = ""

        tag = tag.strip()
        info = info.strip()
        ret.append({
            "severity": flag,
            "component": component,
            "tag": tag,
            "info": info
        })
    return ret


def lint(path, pedantic=False, info=False, experimental=False):
    args = ["lintian", "--show-overrides"]

    if pedantic:
        args.append("--pedantic")
    if info:
        args.append("-I")
    if experimental:
        args.append("-E")

    args.append(path)

    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        output = e.output
    except OSError as e:
        logger.warning("Failed to execute lintian: %s" % (e))
        raise DputConfigurationError("lintian: %s" % (e))

    return process(output)


def lintian(changes, profile, interface):
    """
    The ``lintian`` checker is a stock dput checker that checks packages
    intended for upload for common mistakes, using the static checking
    tool, `lintian <http://lintian.debian.org/>`.

    Profile key: ``lintian``

    Example profile::

        {
            "run_lintian": true
            "lintian": {
            }
        }

    No keys are current supported, but there are plans to set custom
    ignore lists, etc.
    """
    if "run_lintian" in profile:
        logger.warning("Setting 'run_lintian' is deprecated. "
                       "Please configure the lintian checker instead.")
        if not profile['run_lintian']:  # XXX: Broken. Fixme.
            logger.info("skipping lintian checking, enable with "
                        "run_lintian = 1 in your dput.cf")
            return

    tags = lint(
        changes._absfile,
        pedantic=True,
        info=True,
        experimental=True
    )

    sorted_tags = {}

    for tag in tags:
        if not tag['severity'] in sorted_tags:
            sorted_tags[tag['severity']] = {}
        if tag['tag'] not in sorted_tags[tag['severity']]:
            sorted_tags[tag['severity']][tag['tag']] = tag
    tags = sorted_tags

    # XXX: Make this configurable
    if not "E" in tags:
        return
    for tag in set(tags["E"]):
        print("  - %s: %s" % (tags["E"][tag]['severity'], tag))

    inp = interface.boolean('Lintian Checker',
                            'Upload despite of Lintian finding issues?',
                            default=BUTTON_NO)
    if not inp:
        raise LintianHookException(
            "User didn't own up to the "
            "Lintian issues"
        )
    else:
        logger.warning("Uploading with outstanding Lintian issues.")
