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
CLI User Interface Implementation
"""

import sys
import getpass

from dput.interface import AbstractInterface


class CLInterface(AbstractInterface):
    """
    Concrete implementation of the command line user interface.
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.interface.AbstractInterface.initialize`
        """
        pass  # nothing here.

    def query(self, title, questions):
        """
        See :meth:`dput.interface.AbstractInterface.query`
        """
        ret = []
        for question in questions:
            msg = "%s: " % (question['msg'])
            if question['show']:
                sys.stdout.write(msg)
                ret.append(sys.stdin.readline().strip())
            else:
                ret.append(getpass.getpass(msg))
        return ret

    def shutdown(self):
        """
        See :meth:`dput.interface.AbstractInterface.shutdown`
        """
        pass  # nothing here.
