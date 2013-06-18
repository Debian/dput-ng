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
import os.path
from dput.command import AbstractCommand
from dput.exceptions import DcutError
from dput.core import logger, get_local_username
from dput.util import run_command

DM_KEYRING = "/usr/share/keyrings/debian-maintainers.gpg"


class DmCommandError(DcutError):
    pass


def generate_dak_commands_name(profile):
    # for debianqueued: $login-$timestamp.commands
    # for dak: $login-$timestamp.dak-commands
    the_file = "%s-%s.dak-commands" % (get_local_username(), int(time.time()))
    # XXX: override w/ DEBEMAIL (if DEBEMAIL is @debian.org?)
    logger.trace("Commands file will be named %s" % (the_file))
    return the_file


class DmCommand(AbstractCommand):
    def __init__(self, interface):
        super(DmCommand, self).__init__(interface)
        self.cmd_name = "dm"
        self.cmd_purpose = "manage Debian Mantainer (DM) permissions"

    def generate_commands_name(self, profile):
        return generate_dak_commands_name(profile)

    def register(self, parser, **kwargs):
        parser.add_argument('--uid', action='store', default=None, dest="dm",
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
        fh.write("\n")  # yes, this newline matters
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
        if args.force:
            return

        if not os.path.exists(DM_KEYRING):
            raise DmCommandError(
                "To manage DM permissions, the `debian-keyring' "
                "keyring package must be installed. "
                "File %s does not exist" % (DM_KEYRING)
            )
            return

        # I HATE embedded functions. But OTOH this function is not usable
        # somewhere else, so...
        def pretty_print_list(tuples):
            fingerprints = ""
            for entry in tuples:
                fingerprints += "\n- %s (%s)" % entry
            return fingerprints

        # TODO: Validate input. Packages must exist (i.e. be not NEW)
        (out, err, exit_status) = run_command([
            "gpg", "--no-options",
            "--no-auto-check-trustdb", "--no-default-keyring",
            "--list-key", "--with-colons", "--fingerprint",
            "--keyring", DM_KEYRING, args.dm
        ])
        if exit_status != 0:
            raise DmCommandError("DM fingerprint lookup "
                                 "for argument %s failed. "
                                 "GnuPG returned error: %s" %
                                 (args.dm, err))
        possible_fingerprints = []
        current_uid = None
        next_line_contains_fpr = False
        gpg_out = out.split("\n")
        for line in gpg_out:
            if next_line_contains_fpr:
                assert(line.startswith("fpr"))
                parsed_fingerprint = line.split(":")
                # fpr:::::::::CACE80AE01512F9AE8AB80D61C01F443C9C93C5A:
                possible_fingerprints.append((current_uid,
                                              parsed_fingerprint[9],))
                next_line_contains_fpr = False
                continue

            elif not line.startswith("pub"):
                continue

            else:
                # will give a line like:
                # pub:-:4096:1:7B585B30807C2A87:2011-08-18:::-:
                # Paul Tagliamonte <tag@pault.ag>::scESC:
                # without the newline
                parsed_fingerprint = line.split(":")

                current_uid = parsed_fingerprint[9]
                next_line_contains_fpr = True

        if len(possible_fingerprints) > 1:
            raise DmCommandError("DM argument `%s' is ambiguous. "
                                 "Possible choices:\n%s" %
                                 (args.dm,
                                  pretty_print_list(possible_fingerprints)))

        possible_fingerprints = possible_fingerprints[0]
        logger.info("Picking DM %s with fingerprint %s" %
                    possible_fingerprints)
        args.dm = possible_fingerprints[1]

    def name_and_purpose(self):
        return (self.cmd_name, self.cmd_purpose)
