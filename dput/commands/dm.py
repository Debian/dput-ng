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

import time
import os

from dput.command import AbstractCommand
from dput.exceptions import DcutError
from dput.core import logger


class DmCommandError(DcutError):
    pass


def generate_dak_commands_name(profile):
    # for debianqueued: $login-$timestamp.commands
    # for dak: $login-$timestamp.dak-commands
    the_file = "%s-%s.dak-commands" % (os.getlogin(), int(time.time()))
    logger.trace("Commands file will be named %s" % (the_file))
    return the_file


class DmCommand(AbstractCommand):
    def __init__(self):
        super(DmCommand, self).__init__()
        self.cmd_name = "dm"
        self.cmd_purpose = "manage Debian Mantainer (DM) permissions"

    def generate_commands_name(self, profile):
        return generate_dak_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('--dm', action='store', default=None,
                            help="Name, e-mail or fingerprint of an existing "
                            "Debian Maintainer", required=True)
        parser.add_argument('--allow', metavar="PACKAGES",
                            action='store', default=None,
                            help="Source package(s) where permissions to "
                            "upload should be granted", nargs="*")
        parser.add_argument('--deny', metavar="PACKAGES",
                            action='store', default=None,
                            help="Source package(s) where permissions to "
                            "upload should be denied", nargs="*")

    def produce(self, fh, args):
        fh.write("\n") # yes, this newline matters
        fh.write("Action: %s\n" % (self.cmd_name))
        fh.write("Fingerprint: %s\n" % (args.dm))
        if args.allow:
            fh.write("Allow: ")
            for allowed_packages in args.allow:
                fh.write("%s " % (allowed_packages))
            fh.write("\n")
        if args.deny:
            fh.write("Deny: ")
            for denied_packages in args.deny:
                fh.write("%s " % (denied_packages))
            fh.write("\n")

    def validate(self, args):
        print("validate")
        # TODO: Validate input. Packages must exist (i.e. be not NEW)
        # and translate the --dm argument to a fingerprint (and/or validate it)

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
