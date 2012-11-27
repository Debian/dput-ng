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
Interface implementation.
"""

import abc

"""
A button labeled 'yes'
"""
BUTTON_YES = "yes"
"""
A button labeled 'no'
"""
BUTTON_NO = "no"
"""
A button labeled 'cancel'
"""
BUTTON_CANCEL = "cancel"
"""
A button labeled 'ok'
"""
BUTTON_OK = "ok"
(WIDGET_BOOLEAN, WIDGET_MESSAGE, WIDGET_LIST, WIDGET_QUESTION) = range(4)

# some "shortcuts"
ALL_BUTTONS = [BUTTON_YES, BUTTON_NO, BUTTON_CANCEL, BUTTON_OK]
BUTTON_YES_NO = [BUTTON_YES, BUTTON_NO]
BUTTON_OK_CANCEL = [BUTTON_OK, BUTTON_CANCEL]


class AbstractInterface(object):
    """
    Abstract base class for Concrete implementations of user interfaces.

    The invoking process will instantiate the process, call initialize,
    query (any number of times), and shutdown.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, **kwargs):
        """
        Set up the interface state.
        """
        pass

    def boolean(self, title, message, question_type=BUTTON_YES_NO,
                default=None):
        """
        Display a question returning a boolean value. This is evaluated
        by checking the button return code either to be BUTTON_YES or
        BUTTON_OK
        """
        self.widget_type = WIDGET_BOOLEAN
        self.message = message
        self.question_type = question_type
        self.default = default

    def message(self, title, message, question_type=BUTTON_OK):
        """
        Display a message and a confirmation button when required by the
        interface to make sure the user noticed the message Some interfaces,
        e.g. the CLI may ignore the button.
        """
        self.widget_type = WIDGET_MESSAGE
        self.message = message
        self.question_type = question_type

    def list(self, title, message, selections=[]):
        """
        Display a list of alternatives the user can choose from, returns a
        list of selections.
        """
        self.widget_type = WIDGET_LIST
        self.message = message
        self.selection = selections

    def question(self, title, message, echo_input=True):
        """
        Query for user input. The input is returned literally
        """
        self.widget_type = WIDGET_QUESTION
        self.message = message
        self.echo_input = True

    def password(self, title, message):
        """
        Query for user input. The input is returned literally but not printed
        back. This is a shortcut to
        :meth:`dput.interface.AbstractInterface.question` with echo_input
        defaulting to False
        """
        self.question(title, message, echo_input=False)

    @abc.abstractmethod
    def shutdown(self):
        """
        Get rid of everything, close out.
        """
        pass
