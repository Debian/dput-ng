# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2013 Luca Falavigna <dktrkranz@debian.org>
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
from dput.profile import load_profile


class DebomaticCommandError(DcutError):
    pass

class BuilddepCommand(AbstractCommand):
    def __init__(self, interface):
        super(BuilddepCommand, self).__init__(interface)
        self.cmd_name = "debomatic-builddep"
        self.cmd_purpose = ("rebuild a source package with Deb-o-Matic adding "
                            "specific build-dependencies")

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-s', '--source', metavar="SOURCE", action='store',
                            default=None, help="source pacakge to rebuild. ",
                            required=True)
        parser.add_argument('-v', '--version', metavar="VERSION",
                            action='store', default=None, help="version of "
                            "the source package to rebuild. ", required=True)
        parser.add_argument('-d', '--distribution', metavar="DISTRIBUTION",
                            action='store', default=None, help="distribution "
                            "which rebuild the package for. ", required=True)
        parser.add_argument('-p', '--packages', metavar="PACKAGES",
                            action='store', default=None, help="packages to "
                            "be installed at compile time. ", required=True)

    def produce(self, fh, args):
        fh.write("Commands:\n")
        fh.write("  builddep %s_%s %s %s\n" % (args.source, args.version,
                                               args.distribution,
                                               args.packages))

    def validate(self, args):
        profile = load_profile(args.host)
        if (not 'allow_debomatic_commands' in profile
                or not profile['allow_debomatic_commands']):
            raise DebomaticCommandError(
                "Deb-o-Matic commands not supported for this profile"
            )

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)

class PorterCommand(AbstractCommand):
    def __init__(self, interface):
        super(PorterCommand, self).__init__(interface)
        self.cmd_name = "debomatic-porter"
        self.cmd_purpose = "generate a porter upload with Deb-o-Matic"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-s', '--source', metavar="SOURCE", action='store',
                            default=None, help="source pacakge to generate a "
                            "porter upload for. ", required=True)
        parser.add_argument('-v', '--version', metavar="VERSION",
                            action='store', default=None, help="version of "
                            "the source package to generate a porter upload "
                            "for. ", required=True)
        parser.add_argument('-d', '--distribution', metavar="DISTRIBUTION",
                            action='store', default=None, help="distribution "
                            "which build the package for. ", required=True)
        parser.add_argument('-m', '--maintainer', metavar="MAINTAINER",
                            action='store', default=None, help="contact to be "
                            "listed in the  Maintainer field. ", required=True)

    def produce(self, fh, args):
        fh.write("Commands:\n")
        fh.write("  porter %s_%s %s %s\n" % (args.source, args.version,
                                             args.distribution,
                                             args.maintainer))

    def validate(self, args):
        profile = load_profile(args.host)
        if (not 'allow_debomatic_commands' in profile
                or not profile['allow_debomatic_commands']):
            raise DebomaticCommandError(
                "Deb-o-Matic commands not supported for this profile"
            )

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)


class RebuildCommand(AbstractCommand):
    def __init__(self, interface):
        super(RebuildCommand, self).__init__(interface)
        self.cmd_name = "debomatic-rebuild"
        self.cmd_purpose = "rebuild a source package with Deb-o-Matic"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-s', '--source', metavar="SOURCE", action='store',
                            default=None, help="source pacakge to rebuild. ",
                            required=True)
        parser.add_argument('-v', '--version', metavar="VERSION",
                            action='store', default=None, help="version of "
                            "the source package to rebuild. ", required=True)
        parser.add_argument('-d', '--distribution', metavar="DISTRIBUTION",
                            action='store', default=None, help="distribution "
                            "which rebuild the package for. ", required=True)
        parser.add_argument('-o', '--origin', metavar="ORIGIN", action='store',
                            default='', help="distribution to pick source "
                            "package from. ")

    def produce(self, fh, args):
        fh.write("Commands:\n")
        fh.write("  rebuild %s_%s %s %s\n" % (args.source, args.version,
                                              args.distribution, args.origin))

    def validate(self, args):
        profile = load_profile(args.host)
        if (not 'allow_debomatic_commands' in profile
                or not profile['allow_debomatic_commands']):
            raise DebomaticCommandError(
                "Deb-o-Matic commands not supported for this profile"
            )

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)


class RmCommand(AbstractCommand):
    def __init__(self, interface):
        super(RmCommand, self).__init__(interface)
        self.cmd_name = "debomatic-rm"
        self.cmd_purpose = "remove a file from Deb-o-Matic upload queue"

    def generate_commands_name(self, profile):
        return generate_debianqueued_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('-f', '--file', metavar="FILENAME", action='store',
                            default=None, help="file to be removed. "
                            "The argument could contain Unix shell patterns.",
                            nargs="+", required=True)

    def produce(self, fh, args):
        fh.write("Commands:\n")
        for rm_file in args.file:
            fh.write("  rm %s\n" % rm_file)

    def validate(self, args):
        profile = load_profile(args.host)
        if (not 'allow_debomatic_commands' in profile
                or not profile['allow_debomatic_commands']):
            raise DebomaticCommandError(
                "Deb-o-Matic commands not supported for this profile"
            )

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
