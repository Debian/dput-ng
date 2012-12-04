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


class UploadCommand(AbstractCommand):
    def __init__(self, interface):
        super(UploadCommand, self).__init__(interface)
        self.cmd_name = "upload"
        self.cmd_purpose = "Upload an existing file as is"

    def generate_commands_name(self, profile):
        pass

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            dest='upload_file', default=None, required=True,
                            help="file name to be uploaded")

    def produce(self, fh, args):
        return

    def validate(self, args):
        return

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
