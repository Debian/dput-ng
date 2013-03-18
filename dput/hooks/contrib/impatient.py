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
Tell you when dinstall is next
"""

import datetime as dt
import urllib2
import time
import re


URL_ROOT = "http://ftp-master.debian.org/dinstall.html"


def check_next_install(changes, profile, interface):
    """
    """
    #data = urllib2.urlopen(URL_ROOT).read()
    #times = re.finditer(r"\d{2}:\d{2}", data)
    # XXX: Perhaps re-do it this way? Perhaps?
    times = ['01:52', '07:52', '13:52', '19:52']
    now = dt.datetime.utcnow()
    for t in times:
        day, month, year = (dt.datetime.strftime(now, x)
                            for x in ["%d", "%m", "%Y"])
        t = "%s %s %s %s" % (t, day, month, year)
        nt = dt.datetime.strptime(t, "%H:%M %d %m %Y")
        d = nt - now
        if d.total_seconds() > 0:
            interface.message("next dinstall",
                              "Next dinstall run in %s" % d)
            break
