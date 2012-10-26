#!/usr/bin/env python
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

import dput.profile
import sys

from dput.util import obj_docs
from dput.exceptions import DputConfigurationError, InvalidConfigError


def host_list():
    default = dput.profile.load_profile(None)
    print
    print "Default method: %s" % (default['method'])
    print
    for config in dput.profile.profiles():
        obj = dput.profile.load_profile("%s:%s" % (config, config))
        #                               ^^^^^^ fake arg for others
        if not "fqdn" in obj:  # likely localhost
            obj['fqdn'] = 'localhost'

        string = "{name} => {fqdn}  (Upload method: {method})".format(**obj)
        print string
    print

    sys.exit(0)

def print_conf():
    print "Unimplemented."
    sys.exit(0)

def show_class_list(show):
    print(show)

def show_class(checker, processor):
    if checker:
        klass = "checkers"
        thing = checker
    elif processor:
        klass = "processors"
        thing = processor

    try:
        docs = obj_docs(klass, thing)
        if docs is None:
            print "Sorry, the author of that module didn't provide documentation."
        else:
            print docs
    except DputConfigurationError as e:
        print "Error with the config file:"
        print e
    except InvalidConfigError as e:
        print "Invalid config file:"
        print e
