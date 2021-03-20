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

KEYRINGS = [
    "/usr/share/keyrings/debian-maintainers.gpg",
    "/usr/share/keyrings/debian-nonupload.gpg"
]

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
                            "Debian Maintainer. Use a full fingerprint together "
                            "with --force if you want to bypass any argument "
                            "validation, causing dcut to take the argument "
                            "literally as is.", required=True)
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

        if not all((os.path.exists(keyring) for keyring in KEYRINGS)):
            raise DmCommandError(
                "To manage DM permissions, the `debian-keyring' "
                "keyring package must be installed."
            )

        # I HATE embedded functions. But OTOH this function is not usable
        # somewhere else, so...
        def pretty_print_list(tuples):
            fingerprints = ""
            for entry in tuples:
                fingerprints += "\n- %s (%s)" % entry
            return fingerprints

        # I don't mind embedded functions  ;3
        def flatten(it):
            return [ item for nested in it for item in nested ]

        # TODO: Validate input. Packages must exist (i.e. be not NEW)
        cmd =[
            "gpg", "--no-options",
            "--no-auto-check-trustdb", "--no-default-keyring",
            "--list-key", "--with-colons", "--fingerprint"
        ] + flatten(([ "--keyring", keyring] for keyring in KEYRINGS)) + [ args.dm ]

        (out, err, exit_status) = run_command(cmd)
        if exit_status != 0:
            logger.warning("")
            logger.warning("There was an error looking up the DM's key")
            logger.warning("")
            logger.warning(" dput-ng uses the DM keyring in /usr/share/keyrings/")
            logger.warning(" as the keyring to pull full fingerprints from.")
            logger.warning("")
            logger.warning(" Please ensure your keyring is up to date:")
            logger.warning("")
            logger.warning("   sudo apt-get install debian-keyring")
            logger.warning("")
            logger.warning(" Or, if you can not get the keyring, you may use their")
            logger.warning(" full fingerprint (without spaces) and pass the --force")
            logger.warning(" argument in. This goes to dak directly, so try to")
            logger.warning(" pay attention to formatting.")
            logger.warning("")
            logger.warning("")
            raise DmCommandError("DM fingerprint lookup "
                                 "for argument %s failed. "
                                 "GnuPG returned error: %s" %
                                 (args.dm, err))
        possible_fingerprints = []
        current_uid = None
        current_fpr = None
        waiting_for_pub = True
        gpg_out = out.split("\n")
        # With GnuPG 2 output will be something like this:
        # tru::1:1526653314:1527815734:3:1:5
        # pub:u:4096:1:4B043FCDB9444540:1353241761:1830253453::u:::scESCA::::::23::0:
        # fpr:::::::::66AE2B4AFCCF3F52DA184D184B043FCDB9444540:
        # uid:u::::1502192653::C2DB9DA864342EDE417ABE122D8983D3BF051A22::Mattia Rizzolo <mattia@mapreri.org>::::::::::0:
        for line in gpg_out:
            if current_uid and current_fpr:
                # if the previous iteration got us a useful key...
                possible_fingerprints.append((current_uid, current_fpr))
                current_uid = None
                current_fpr = None
                waiting_for_pub = True

            if waiting_for_pub and not line.startswith("pub"):
                continue
            elif line.startswith("pub"):
                waiting_for_pub = False
                continue
            elif current_fpr is None and line.startswith("fpr"):
                current_fpr = line.split(":")[9]
                continue
            elif current_uid is None and line.startswith("uid"):
                # this only gets the first uid
                current_uid = line.split(":")[9]
                continue

        possible_fingerprints = list(set(possible_fingerprints))
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
