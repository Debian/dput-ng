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
"""
Uploader implementation. The code in here surrounds the uploaders'
implementations, and properly invokes the uploader with correct
arguments, etc.
"""

import os
import abc
import sys
import tempfile
import shutil
from contextlib import contextmanager

import dput.profile
from dput.changes import parse_changes_file
from dput.core import logger, _write_upload_log
from dput.hook import run_pre_hooks, run_post_hooks
from dput.util import (run_command, get_obj)
from dput.overrides import (make_delayed_upload, force_passive_ftp_upload)
from dput.exceptions import (DputConfigurationError, DputError,
                             UploadException)


class AbstractUploader(object):
    """
    Abstract base class for all concrete uploader implementations.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, profile):
        self._config = profile
        interface = 'cli'
        if 'interface' in profile:
            interface = profile['interface']
        logger.trace("Using interface %s" % (interface))
        interface_obj = get_obj('interfaces', interface)
        if interface_obj is None:
            raise DputConfigurationError("No such interface: `%s'" % (
                interface
            ))
        self.interface = interface_obj()
        self.interface.initialize()

    def _pre_hook(self):
        self._run_hook("pre_upload_command")

    def _post_hook(self):
        self._run_hook("post_upload_command")

    def _run_hook(self, hook):
        if hook in self._config and self._config[hook] != "":
            cmd = self._config[hook]
            (output, stderr, ret) = run_command(cmd)
            if ret == -1:
                if not os.path.exists(cmd):
                    logger.warning(
                        "Error: You've set a hook (%s) to run (`%s`), "
                        "but it can't be found (and doesn't appear to exist)."
                        " Please verify the path and correct it." % (
                            hook,
                            self._config[hook]
                        )
                    )
                    return

            sys.stdout.write(output)  # XXX: Fixme
            if ret != 0:
                raise DputError(
                    "Command `%s' returned an error: %s [err=%d]" % (
                        self._config[hook],
                        stderr,
                        ret
                    )
                )

    def __del__(self):
        self.interface.shutdown()

    def upload_write_error(self, e):
        """
        .. warning::
           don't call this.

        please don't call this
        """
        # XXX: Refactor this, please god, refactor this.
        logger.warning("""Upload permissions error

You either don't have the rights to upload a file, or, if this is on
ftp-master, you may have tried to overwrite a file already on the server.

Continuing anyway in case you want to recover from an incomplete upload.
No file was uploaded, however.""")

    @abc.abstractmethod
    def initialize(self, **kwargs):
        """
        Setup the things needed to upload a file. Usually this means creating
        a network connection & authenticating.
        """
        pass

    @abc.abstractmethod
    def upload_file(self, filename, upload_filename=None):
        """
        Upload a single file (``filename``) to the server.
        """
        pass

    @abc.abstractmethod
    def shutdown(self):
        """
        Disconnect and shutdown.
        """
        pass


@contextmanager
def uploader(uploader_method, profile, simulate=True):
    """
    Context-managed uploader implementation.

    Invoke sorta like::

        with uploader() as obj:
            obj.upload_file('filename')

    This will automatically call that object's
    :meth:`dput.uploader.AbstractUploader.initialize`,
    pre-hook, yield the object, call the post hook and invoke it's
    :meth:`dput.uploader.AbstractUploader.shutdown`.
    """
    cls = get_obj('uploaders', uploader_method)

    if not cls:
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

    obj = cls(profile)
    if not simulate or simulate >= 2:
        obj.initialize()
    obj._pre_hook()
    try:
        yield obj
    finally:
        if not simulate:
            obj._post_hook()
        if not simulate or simulate >= 2:
            obj.shutdown()


def determine_logfile(changes, conf, args):
    """
    Figure out what logfile to write to. This is mostly an internal
    implementation. Returns the file to log to, given a changes and
    profile.
    """
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

    if (
        os.access(logfile, os.R_OK) and
        os.stat(logfile).st_size > 0 and
        not args.force
    ):

        raise UploadException("""Package %s was already uploaded to %s
If you want to upload nonetheless, use --force or remove %s""" % (
            changes.get_package_name(),
            conf['name'],
            logfile
        ))

    logger.debug("Writing log to %s" % (logfile))
    return logfile


def should_write_logfile(args):
    return not args.simulate and not args.check_only and not args.no_upload_log


def check_modules(profile):
    if 'hooks' in profile:
        for hook in profile['hooks']:
            obj = get_obj('hooks', hook)
            if obj is None:
                raise DputConfigurationError(
                    "Error: no such hook '%s'" % (
                        hook
                    )
                )


class DputNamespace(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, val):
        self[key] = val


def invoke_dput_simple(changes, host, **kwargs):
    changes = parse_changes_file(changes, os.path.dirname(changes))
    # XXX: Abspath???
    config = {
        "host": host,
        "debug": False,
        "config": None,
        "force": False,
        "simulate": False,
        "check_only": None,
        "no_upload_log": None,
        "full_upload_log": None,
        "delayed": None,
        "passive": None,
    }
    config.update(kwargs)
    config = DputNamespace(config)

    return invoke_dput(changes, config)


def invoke_dput(changes, args):
    """
    .. warning::
       This method may change names. Please use it via :func:`dput.upload`.
       also, please don't depend on args, that's likely to change shortly.

    Given a changes file ``changes``, and arguments to dput ``args``,
    upload a package to the archive that makes sense.

    """
    profile = dput.profile.load_profile(args.host)
    check_modules(profile)

    fqdn = None
    if "fqdn" in profile:
        fqdn = profile['fqdn']
    else:
        fqdn = profile['name']

    logfile = determine_logfile(changes, profile, args)
    tmp_logfile = tempfile.NamedTemporaryFile()
    if should_write_logfile(args):
        full_upload_log = profile["full_upload_log"]
        if args.full_upload_log:
            full_upload_log = args.full_upload_log
        _write_upload_log(tmp_logfile.name, full_upload_log)

    if args.delayed:
        make_delayed_upload(profile, args.delayed)

    if args.simulate:
        logger.warning("Not uploading for real - dry run")

    if args.passive:
        force_passive_ftp_upload(profile)

    logger.info("Uploading %s using %s to %s (host: %s; directory: %s)" % (
        changes.get_package_name(),
        profile['method'],
        profile['name'],
        fqdn,
        profile['incoming']
    ))

    if 'hooks' in profile:
        run_pre_hooks(changes, profile)
    else:
        logger.trace(profile)
        logger.warning("No hooks defined in the profile. "
                       "Not checking upload.")

    # check only is a special case of -s
    if args.check_only:
        args.simulate = 1

    with uploader(profile['method'], profile,
                  simulate=args.simulate) as obj:

        if args.check_only:
            logger.info("Package %s passes all checks" % (
                changes.get_package_name()
            ))
            return

        if args.no_upload_log:
            logger.info("Not writing upload log upon request")

        files = changes.get_files() + [changes.get_changes_file()]
        for path in files:
            logger.info("Uploading %s%s" % (
                os.path.basename(path),
                " (simulation)" if args.simulate else ""
            ))

            if not args.simulate:
                obj.upload_file(path)

        if args.simulate:
            return

        if 'hooks' in profile:
            run_post_hooks(changes, profile)
        else:
            logger.trace(profile)
            logger.warning("No hooks defined in the profile. "
                           "Not post-processing upload.")
    if should_write_logfile(args):
        tmp_logfile.flush()
        shutil.copy(tmp_logfile.name, logfile)
        #print(tmp_logfile.name)
        tmp_logfile.close()
