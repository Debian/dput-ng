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
Base exceptions. All hooks and internal modules should subclass
Exceptions listed here.
"""


class DputError(BaseException):
    """
    Most basic dput error. All other Exceptions must inherit from this
    when it is sensable to do so.
    """
    pass


class DcutError(BaseException):
    pass


class DputConfigurationError(DputError):
    """
    Errors in the parsing or retrieving of configuration files should raise
    an instance of this, or a subclass thereof.
    """
    pass


class NoSuchConfigError(DputError):
    """
    Thrown when dput can not find a Configuration file or block that is
    requested.
    """
    pass


class InvalidConfigError(DputError):
    """
    Config file was loaded properly, but it was missing part of it's
    required fields.
    """
    pass


class ChangesFileException(DputError):
    """
    Thrown when there's an error processing / verifying a .changes file
    (most often via the :class:`dput.changes.Changes` object)
    """
    pass


class DscFileException(DputError):
    """
    Thrown when there's an error processing / verifying a .dsc file
    (most often via the :class:`dput.changes.Dsc` object)
    """
    pass


class UploadException(DputError):
    """
    Thrown when there's an error uploading, or creating an uploader. Usually
    thrown by a subclass of the :class:`dput.uploader.AbstractUploader`
    """
    pass


class HookException(DputError):
    """
    Thrown when there's an error checking, or creating a checker. Usually
    thrown by a checker invoked by :class:`dput.checker.run_hooks`.
    """
    pass


class NoSuchHostError(DputError):
    """
    Thrown when the network doesn't allow us to connect to a host.
    """
    pass
