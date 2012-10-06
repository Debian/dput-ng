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

import subprocess
from collections import defaultdict

from dput.core import logger
from dput.exceptions import CheckerException


class LintianCheckerException(CheckerException):
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

    return process(output)


def lintian(changes, dputcf, profile):
    if "run_lintian" in dputcf:
        if not dputcf['run_lintian']:
            logger.info("skipping lintian checking, enable with "
                        "run_lintian = 1 in your dput.cf")
            return

    tags = lint(
        changes._absfile,
        pedantic=True,
        info=True,
        experimental=True
    )

    counts = defaultdict(int)
    tcounts = [x['severity'] for x in tags]
    for entry in tcounts:
        counts[entry] += 1

    if counts['W'] > 0:
        raise LintianCheckerException("Too many warnings (%s)" % (
            counts['W']
        ))
