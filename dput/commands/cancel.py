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

from dput.command import AbstractCommand
from dput.exceptions import DcutError
from dput.core import logger, get_local_username


class CancelCommandError(DcutError):
    pass


def generate_debianqueued_commands_name(profile):
    # for debianqueued: $login-$timestamp.commands
    # for dak: $login-$timestamp.dak-commands
    the_file = "%s-%s.commands" % (get_local_username(), int(time.time()))
    logger.trace("Commands file will be named %s" % (the_file))
    return the_file


class CancelCommand(AbstractCommand):
    def __init__(self, interface):
        super(CancelCommand, self).__init__(interface)
        self.cmd_name = "cancel"
        self.cmd_purpose = "cancel a deferred upload"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            default=None, help="file name to be removed",
                            nargs="+", required=True)

    def produce(self, fh, args):
        fh.write("Commands:\n")
        for rm_file in args.file:
            fh.write("  %s %s\n" % (
                self.cmd_name,
                rm_file
            ))

    def validate(self, args):
        # TODO: Validate input. It must be a changes file reference
        #       Aside we cannot do much. The file is remote, so we cannot
        #       process it
        pass

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
