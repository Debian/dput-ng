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
from dput.commands.cancel import generate_debianqueued_commands_name


class RmCommandError(DcutError):
    pass


class RmCommand(AbstractCommand):
    def __init__(self):
        super(RmCommand, self).__init__()
        self.cmd_name = "rm"
        self.cmd_purpose = "remove a file from the upload queue"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            default=None, help="file name to be removed",
                            nargs="+")
        parser.add_argument('--searchdirs', action='store_true', default=None,
                            help="Search in all directories for the given"
                            " file. Only supported for files in the DELAYED"
                            " queue.")

    def produce(self, fh, args):
        fh.write("Commands:\n")
        for rm_file in args.file:
            fh.write("  %s %s %s\n" % (
                                     self.cmd_name,
                                     "--searchdirs" if args.searchdirs else "",
                                     rm_file))

    def validate(self, args):
        print("validate")
        # TODO: argument can be either a path or a base name, but then the user
        #       most likely wants to add --searchdirs

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
