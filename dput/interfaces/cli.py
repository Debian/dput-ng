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

from dput.interface import *


class CLInterface(AbstractInterface):
    """
    Concrete implementation of the command line user interface.
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.interface.AbstractInterface.initialize`
        """
        pass  # nothing here.

    def button_to_str(self, button):
        for item in ALL_BUTTONS:
            if item == button:
                return item
        assert(False)

    def str_to_button(self, str_button, default):
        # return default when no input was supplied
        if default and not str_button:
            return default
        # compare literally
        if str_button in ALL_BUTTONS:
            return str_button
        # guess input until only one choice is left
        assert(False)


    def boolean(self, title, message, question_type=BUTTON_YES_NO, default=None):
        super(CLInterface, self).boolean(title, message, question_type)

        choices = ""
        question_len = len(question_type)
        for question in question_type:
            button_name = self.button_to_str(question)
            if question == default:
                button_name = button_name.upper()
            choices += button_name
            question_len -= 1
            if question_len:
                choices += ", "
        input = self.question(title, "%s [%s]" % (message, choices))
        self.str_to_button(input, default)
        if input in (BUTTON_OK, BUTTON_YES):
            return True
        return False

    def message(self, title, message, question_type=BUTTON_OK):
        super(CLInterface, self).message(title, message, question_type)
        # XXX implement when needed. No use so far
        assert(False)

    def list(self, title, message, selections=[]):
        super(CLInterface, self).list(title, message, selections)
        # XXX implement when needed. No use so far
        assert(False)

    def question(self, title, message, echo_input=True):
        """
        See :meth:`dput.interface.AbstractInterface.query`
        """
        super(CLInterface, self).question(title, message, echo_input)

        message = "%s: " % (message)
        if title:
            sys.stdout.write("%s: " % (title))
        if echo_input:
            sys.stdout.write(message)
            return sys.stdin.readline().strip()
        else:
            return getpass.getpass(message)

    def shutdown(self):
        """
        See :meth:`dput.interface.AbstractInterface.shutdown`
        """
        pass  # nothing here.
