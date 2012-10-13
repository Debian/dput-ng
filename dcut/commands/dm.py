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

from dcut.uploader import AbstractCommand
from dput.exceptions import DcutError

class DmCommandError(DcutError):
    pass

class DmCommand(AbstractCommand):
    def __init__(self):
        super(DmCommand, self).__init__()
        self.cmd_name = "dm"
        self.cmd_purpose = "manage Debian Mantainer (DM) permissions"

    def register(self, parser):
        parser.add_argument('--dm', action='store', default=None,
                            help="Name, e-mail or fingerprint of an existing "
                            "Debian Maintainer", nargs=1)
        parser.add_argument('--allow', metavar="PACKAGES",
                            action='append', default=None,
                            help="Source package(s) where permissions to "
                            "upload should be granted", nargs="+")
        parser.add_argument('--deny', metavar="PACKAGES",
                            action='append', default=None,
                            help="Source package(s) where permissions to "
                            "upload should be denied", nargs="+")

    def produce(self, fh):
        print("produce")

    def validate(self, **kwargs):
        print("validate")

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
