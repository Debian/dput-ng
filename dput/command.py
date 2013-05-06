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
# XXX: DOCUMENT ME.

import abc
import os
import tempfile
import email.utils
import shutil
import pwd
import socket

import dput.profile
from dput.util import get_obj_by_name, get_configs, run_command
from dput.core import logger, get_local_username
from dput.exceptions import (UploadException, DputConfigurationError,
                             DcutError, NoSuchConfigError)
from dput.overrides import force_passive_ftp_upload
from dput.uploader import uploader


class AbstractCommand(object):
    """
    Abstract base class for all concrete dcut command implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, interface):
        self.cmd_name = None
        self.cmd_purpose = None
        self.interface = interface

    @abc.abstractmethod
    def register(self, parser, **kwargs):
        pass

    @abc.abstractmethod
    def produce(self, fh, args):
        pass

    @abc.abstractmethod
    def validate(self, args):
        pass

    @abc.abstractmethod
    def name_and_purpose(self):
        pass

    @abc.abstractmethod
    def generate_commands_name(self, profile):
        pass


def find_commands():
    return get_configs('commands')


def load_commands(profile):
    commands = []
    for command in profile['valid_commands']:
        logger.debug("importing command: %s" % (command))
        try:
            # XXX: Stubbed the profile for now. That ignores any user choice
            #      on the profile.
            #      Reason being that the profile and the argument parser is a
            #      transitive circular dependency. That should be fixed at some
            #      point.
            with get_obj_by_name('commands', command, {}) as(obj, interface):
                commands.append(obj(interface))
        except NoSuchConfigError:
            raise DputConfigurationError("No such command: `%s'" % (command))

    return commands


def write_header(fh, profile, args):

    email_address = os.environ.get("DEBEMAIL", None)
    if email_address is None:
        email_address = os.environ.get("EMAIL", None)

    name = os.environ.get("DEBFULLNAME", None)

    if not name:
        pwd_entry = pwd.getpwnam(get_local_username())
        gecos_name = pwd_entry.pw_gecos.split(",", 1)
        if len(gecos_name) > 1:
            name = gecos_name[0]
        else:
            name = pwd_entry.pw_gecos
    if not email_address:
        email_address = socket.getfqdn(socket.gethostname())

    if args.maintainer:
        (name, email_address) = email.utils.parseaddr(args.maintainer)

    logger.debug("Using %s <%s> as uploader identity" % (name, email_address))

    if not name or not email_address:
        raise DcutError("Your name or email could not be retrieved."
                        "Please set DEBEMAIL and DEBFULLNAME or provide"
                        " a full identity through --maintainer")

    fh.write("Archive: %s\n" % (profile['fqdn']))
    if name and email_address:
        fh.write("Uploader: %s <%s>\n" % (name, email_address))
    return (name, email_address)


def sign_file(filename, keyid=None, profile=None, name=None, email=None):
    logger.debug("Signing file %s - signature hints are key: %s, "
                 "name: %s, email: %s" % (filename, keyid, name, email))

    gpg_path = "gpg"
    if keyid:
        identity_hint = keyid
    else:
        # hard to see here, but name and email is  guaranteed to be set in
        # write_header()
        if name:
            identity_hint = name
        if email:
            identity_hint += " <%s>" % (email)

    logger.trace("GPG identity hint: %s" % (identity_hint))

    (gpg_output, gpg_output_stderr, exit_status) = run_command([
        gpg_path,
        "--default-key", identity_hint,
        "--status-fd", "1",
        "--sign", "--armor", "--clearsign",
        filename
    ])

    if exit_status == -1:
        raise DcutError("Unknown problem while making cleartext signature")

    if exit_status != 0:
        raise DcutError("Failed to make cleartext signature "
                        "to commands file:\n%s" % (gpg_output_stderr))

    if gpg_output.count('[GNUPG:] SIG_CREATED'):
        pass
    else:
        raise DcutError("Failed to make cleartext signature:\n%s" %
                        (gpg_output_stderr))

    os.unlink(filename)
    shutil.move("%s.asc" % (filename), filename)


def upload_commands_file(filename, upload_filename, profile, args):
    with uploader(profile['method'], profile, simulate=args.simulate) as obj:
        logger.info("Uploading %s to %s" % (
            upload_filename,
            profile['name']
        ))
        obj.upload_file(filename, upload_filename=upload_filename)


def invoke_dcut(args):
    profile = dput.profile.load_profile(args.host)

    fqdn = None
    if 'fqdn' in profile:
        fqdn = profile['fqdn']

    if not 'allow_dcut' in profile or not profile['allow_dcut']:
        raise UploadException("Profile %s does not allow command file uploads"
                              "Please set allow_dcut=1 to allow such uploads")

    logger.info("Uploading commands file to %s (incoming: %s)" % (
        fqdn or profile['name'],
        profile['incoming']
    ))

    if args.simulate:
        logger.warning("Not uploading for real - dry run")

    command = args.command
    assert(issubclass(type(command), AbstractCommand))
    command.validate(args)

    if args.passive:
        force_passive_ftp_upload(profile)

    upload_path = None
    fh = None
    upload_filename = command.generate_commands_name(profile)
    try:
        if command.cmd_name == "upload":
            logger.debug("Uploading file %s as is to %s" % (args.upload_file,
                                                            profile['name']))
            if not os.access(args.upload_file, os.R_OK):
                raise DcutError("Cannot access %s: No such file" % (
                    args.upload_file
                ))
            upload_path = args.upload_file
        else:
            fh = tempfile.NamedTemporaryFile(mode='w+r', delete=False)
            (name, email) = write_header(fh, profile, args)
            command.produce(fh, args)
            fh.flush()
            #print fh.name
            fh.close()

            signing_key = None
            if "default_keyid" in profile:
                signing_key = profile["default_keyid"]
            if args.keyid:
                signing_key = args.keyid

            sign_file(fh.name, signing_key, profile, name, email)
            upload_path = fh.name

        if not args.simulate and not args.output:
            upload_commands_file(upload_path, upload_filename, profile, args)
        elif args.output and not args.simulate:
            if os.access(args.output, os.R_OK):
                logger.error("Not writing %s: File already exists" % (
                    args.output
                ))
                # ... but intentionally do nothing
                # TODO: or raise exception?
                return
            shutil.move(fh.name, args.output)
        elif args.simulate:
            pass
        else:
            # we should *never* come here
            assert(False)

    finally:
        if fh and os.access(fh.name, os.R_OK):
            os.unlink(fh.name)
