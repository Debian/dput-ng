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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import re
import os
import abc
import sys
from contextlib import contextmanager

import dput.profile
from dput.core import logger
from dput.overrides import (make_delayed_upload, force_passive_ftp_upload)
from dput.checker import run_checker
from dput.util import (run_command, get_obj)
from dput.exceptions import (DputConfigurationError, DputError,
                             UploadException)


class AbstractUploader(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, profile):
        self._config = profile
        interface = 'cli'
        if 'interface' in profile:
            interface = profile['interface']
        logger.debug("Using interface %s" % (interface))
        interface = get_obj('interfaces', interface)
        if interface is None:
            raise DputConfigurationError("No such interface: `%s'" % (
                interface
            ))
        self._interface = interface()

    def prompt_ui(self, *args, **kwargs):
        self._interface.initialize()
        ret = self._interface.query(*args, **kwargs)
        self._interface.shutdown()
        return ret

    def _pre_hook(self):
        self._run_hook("pre_upload_command")

    def _post_hook(self):
        self._run_hook("post_upload_command")

    def _run_hook(self, hook):
        if hook in self._config and self._config[hook] != "":
            (output, stderr, ret) = run_command(self._config[hook])
            sys.stdout.write(output)  # XXX: Fixme
            if ret != 0:
                raise DputError(
                    "Command `%s' returned an error: %s [err=%d]" % (
                        self._config[hook],
                        stderr,
                        ret
                    )
                )

    def upload_write_error(self, e):
        logger.warning("""Upload permissions error

You either don't have the rights to upload a file, or, if this is on
ftp-master, you may have tried to overwrite a file already on the server.

Continuing anyway in case you want to recover from an incomplete upload.
No file was uploaded, however.""")

    @abc.abstractmethod
    def initialize(self, **kwargs):
        pass

    @abc.abstractmethod
    def upload_file(self, filename):
        pass

    @abc.abstractmethod
    def shutdown(self):
        pass


@contextmanager
def uploader(uploader_method, profile):
    """
    Rent-a-uploader :)
    """
    klass = get_obj('uploaders', uploader_method)

    if not klass:
        logger.error(
            "Failed to resolve method %s to an uploader class" % (
                uploader_method
            )
        )
        raise DputConfigurationError(
            "Failed to resolve method %s to an uploader class" % (
                uploader_method
            )
        )

    obj = klass(profile)
    obj.initialize()
    obj._pre_hook()
    try:
        yield obj
    finally:
        obj._post_hook()
        obj.shutdown()


class BadDistributionError(UploadException):
    pass


def determine_logfile(changes, conf, args):
    # dak requires '<package>_<version>_<[a-zA-Z0-9+-]+>.changes'

    # XXX: Correct --force behavior
    logfile = changes.get_changes_file()  # XXX: Check for existing one
    xtn = ".changes"
    if logfile.endswith(xtn):
        logfile = "%s.%s.upload" % (logfile[:-len(xtn)], conf['name'])
    else:
        raise UploadException("File %s does not look like a .changes file" % (
            changes.get_filename()
        ))

    # XXX: ugh. I really hope nobody every tries to localize dput.
    if os.access(logfile, os.R_OK) and not args.force:
        raise UploadException("""Package %s was already uploaded to %s
If you want to upload nonetheless, use --force or remove %s""" %
    (changes.get_package_name(), conf['name'], logfile))

    logger.debug("Writing log to %s" % (logfile))
    return logfile


def invoke_dput(changes, args):  # XXX: Name sucks, used under a different name
#                                        elsewhere, try again.
    profile = dput.profile.load_profile(args.host)

    fqdn = profile['fqdn']
    logfile = determine_logfile(changes, profile, args)

    logger.info("Uploading to: %s" % (fqdn))

    # XXX: This function is huge, let's break this up!

    # TODO: This function does not correctly handles distributions
    #       which is different to allowed_distributions. Moreover, this should
    #       be a checker instead.
    suite = changes['Distribution']
    srgx = profile['allowed_distributions']
    if re.match(srgx, suite) is None:
        raise BadDistributionError("'%s' doesn't match '%s'" % (
            suite,
            srgx
        ))

    if args.simulate:
        logger.warning("Not uploading for real - dry run")

    if args.delayed:
        make_delayed_upload(profile, args.delayed)

    if args.passive:
        force_passive_ftp_upload(profile)

    if 'checkers' in profile:
        for checker in profile['checkers']:
            logger.info("Running checker %s" % (checker))
            run_checker(checker, changes, profile)
    else:
        logger.debug(profile)
        logger.warning("No checkers defined in the profile. "
                       "Not checking upload.")

    logger.info("Uploading %s to %s (%s)" % (
        changes.get_package_name(),
        fqdn or profile['name'],
        profile['incoming']
    ))

    # XXX: This does not work together with --check-only and --simulate
    # We cannot use with(the_logfile) as an outermost condition
    # Also, the _contents_ of the log-file maybe should contain the logger
    # output?
    with open(logfile, 'w') as log:
        with uploader(profile['method'], profile) as obj:
            for path in changes.get_files() + [changes.get_changes_file(), ]:
                logger.info("Uploading %s => %s" % (
                    os.path.basename(path),
                    profile['name']
                ))
                if not args.simulate:
                    obj.upload_file(path)
                log.write(
                    "Successfully uploaded %s to %s for %s.\n" % (
                        os.path.basename(path),
                        profile['fqdn'] or profile['name'],
                        profile['name']
                    )
                )
