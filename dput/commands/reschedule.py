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


class RescheduleCommandError(DcutError):
    pass


class RescheduleCommand(AbstractCommand):
    def __init__(self, interface):
        super(RescheduleCommand, self).__init__(interface)
        self.cmd_name = "reschedule"
        self.cmd_purpose = "reschedule a deferred upload"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            default=None, help="file name to be rescheduled",
                            nargs=1, required=True)
        parser.add_argument('-d', '--days', metavar="DAYS", action='store',
                            default=None, help="reschedule for DAYS days."
                            " Takes an argument from 0 to 15", type=int,
                            choices=range(0, 16), required=True)

    def produce(self, fh, args):
        fh.write("Commands:\n")
        for rm_file in args.file:
            fh.write("  %s %s %s-day\n" % (
                self.cmd_name,
                rm_file,
                args.days
            ))

    def validate(self, args):
        # TODO: any todos here?
        pass

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
