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

__license__ = "GPL-2+"
__appname__ = "dput"
__authors__ = [
    "Arno Töll <arno@debian.org>",
    "Paul Tagliamonte <paultag@debian.org>"
]

from dput.uploader import invoke_dput_simple as upload
from dput.uploader import invoke_dput as upload_package  # NOQA
"""
See :func:`dput.uploader.invoke_dput`.
"""

from dput.command import invoke_dcut as upload_command  # NOQA
"""
See :func:`dput.command.invoke_dcut`.
"""
