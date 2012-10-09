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

why = """Package: release.debian.org
Severity: normal
User: release.debian.org@packages.debian.org
Usertags: unblock

please unblock package {srcpkg}

{why}

unblock {srcpkg}/{version}
"""

def unblock(changes, profile, interface):
    info = {
        'srcpkg': changes['Source'],
        'version': changes['Version'],
        'why': "You will live a long, healthy, happy life "
               "and make bags of money."
    }
    # XXX: this is utter crap, fixme.
    print "============ [UNBLOCK TEMPLATE] ============"
    print why.format(**info)
    print "============ [UNBLOCK TEMPLATE] ============"
