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
import os.path
from dput.command import AbstractCommand
from dput.exceptions import DcutError
from dput.core import logger
from dput.util import run_command
from dput.commands.dm import generate_dak_commands_name


class BreakTheArchiveCommandCommandError(DcutError):
    pass


class BreakTheArchiveCommand(AbstractCommand):
    def __init__(self):
        super(BreakTheArchiveCommand, self).__init__()
        self.cmd_name = "break-the-archive"
        self.cmd_purpose = "break the archive (no, really)"

    def generate_commands_name(self, profile):
        return generate_dak_commands_name(profile)

    def register(self, parser, **kwargs):
        pass

    def produce(self, fh, args):
        fh.write("\n")  # yes, this newline matters
        fh.write("Action: %s\n" % (self.cmd_name))

    def validate(self, args):
        pass

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
