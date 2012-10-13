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

from dput.command import AbstractCommand
from dput.exceptions import DcutError

class DmCommandError(DcutError):
    pass

class DmCommand(AbstractCommand):
    def __init__(self):
        super(DmCommand, self).__init__()
        self.cmd_name = "dm"
        self.cmd_purpose = "manage Debian Mantainer (DM) permissions"

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
        fh.write("Action: %s\n" % (self.cmd_name))
        fh.write("Fingerprint: %s\n" % (args.dm))
        if args.allow:
            for allowed_packages in args.allow:
                fh.write("Allow: %s %s\n" % (
                                             self.cmd_name,
                                             allowed_packages))
        if args.deny:
            for denied_packages in args.deny:
                fh.write("Deny: %s %s\n" % (
                                            self.cmd_name,
                                            denied_packages))

    def validate(self, args):
        print("validate")

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
