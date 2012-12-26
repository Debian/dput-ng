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
from dput.changes import Changes
from dput.core import logger
# XXX: Generate rm from .changes?


class RmCommandError(DcutError):
    pass


class RmCommand(AbstractCommand):
    def __init__(self, interface):
        super(RmCommand, self).__init__(interface)
        self.cmd_name = "rm"
        self.cmd_purpose = "remove a file from the upload queue"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            default=None, help="file to be removed. "
                            "If the argument is a CHANGES file, a rm command "
                            "for all .deb packages in it is created",
                            nargs="+", required=True)
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
                rm_file
            ))

    def validate(self, args):
        # TODO: argument can be either a path or a base name, but then the user
        #       most likely wants to add --searchdirs

        file_list = []
        if args.file:
            for argument in args.file:
                if argument.endswith("changes"):
                    # force searchdirs
                    args.searchdirs = True
                    changes_file = Changes(filename=argument)
                    file_list += changes_file.get_files()
                    file_list.append(changes_file.get_filename())
                    logger.info("Expanding package list for removals to: %s" %
                                reduce(lambda x, xs: xs + ", " + x, file_list))
                    args.file = file_list
        else:
            raise RmCommandError("No file to be removed supplied?")

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
