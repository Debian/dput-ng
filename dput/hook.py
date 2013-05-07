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
Implementation of the interface to run a hook.
"""

from dput.util import obj_docs, run_func_by_name, load_config, validate_object
from dput.core import logger

try:
    # Optional clojure-py integration.
    import clojure.main  # NOQA
except ImportError:
    logger.trace("No clojure support :(")

try:
    # Optional hy integration.
    import hy  # NOQA
except ImportError:
    logger.trace("No hython support :(")


def hook_docs(hook):
    return obj_docs('hooks', hook)


def get_hooks(profile):
    for hook in profile['hooks']:
        conf = load_config('hooks', hook)
        validate_object('plugin', conf, 'hooks/%s' % (hook))
        yield (hook, conf)


def run_pre_hooks(changes, profile):
    for name, hook in get_hooks(profile):
        if 'pre' in hook and hook['pre']:
            run_hook(name, hook, changes, profile)
        if 'pre' not in hook and 'post' not in hook:
            logger.warning("Hook: %s has no pre/post ordering. Assuming "
                           "pre.")
            run_hook(name, hook, changes, profile)


def run_post_hooks(changes, profile):
    for name, hook in get_hooks(profile):
        if 'post' in hook and hook['post']:
            run_hook(name, hook, changes, profile)


def run_hook(name, hook, changes, profile):
    """
    Run a hook (by the name of ``hook``) against the changes file (by
    the name of ``changes``), with the upload profile (named ``profile``).

    args:
        ``hook`` (str) string of the hook (which is the name of
        the JSON file which contains the hook def)

        ``changes`` (:class:`dput.changes.Changes`) changes file that the
            hook should be run against.

        ``profile`` (dict) dictionary of the profile that will help guide
            the hook's runtime.
    """
    logger.info("running %s: %s" % (name, hook['description']))
    return run_func_by_name('hooks', name, changes, profile)
